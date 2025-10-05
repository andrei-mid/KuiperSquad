from flask import Flask, render_template, request, redirect, url_for
import requests
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import folium
import os
import time

app = Flask(__name__)
API_KEY = "WhNlUOY4qeJRBt60QSdxHbmjueP4j00M2RYD1T4k"

# -------------------- FUNCȚII UTILITARE --------------------
def get_asteroid_list():
    url = f"https://api.nasa.gov/neo/rest/v1/neo/browse?api_key={API_KEY}"
    data = requests.get(url).json()
    asteroids = data['near_earth_objects']
    return [(a['name'], a['id']) for a in asteroids]

def get_gif_filename(asteroid_id):
    safe_name = "".join(c if c.isalnum() else "_" for c in asteroid_id)
    return f"static/{safe_name}.gif"

# -------------------- CALCULE ORBITĂ --------------------
def calculate_orbit(asteroid):
    orbit = asteroid.get('orbital_data', {})
    a = float(orbit.get('semi_major_axis', '1'))
    e = float(orbit.get('eccentricity', '0'))
    i = np.radians(float(orbit.get('inclination', '0')))
    Omega = np.radians(float(orbit.get('ascending_node_longitude', '0')))
    omega = np.radians(float(orbit.get('perihelion_argument', '0')))

    theta = np.linspace(0, 2*np.pi, 500)
    r = (a*(1 - e**2)) / (1 + e*np.cos(theta))
    x, y, z = r*np.cos(theta), r*np.sin(theta), np.zeros_like(theta)

    R1 = np.array([[np.cos(Omega), -np.sin(Omega), 0],
                   [np.sin(Omega),  np.cos(Omega), 0],
                   [0,0,1]])
    R2 = np.array([[1,0,0],
                   [0,np.cos(i),-np.sin(i)],
                   [0,np.sin(i), np.cos(i)]])
    R3 = np.array([[np.cos(omega), -np.sin(omega),0],
                   [np.sin(omega),  np.cos(omega),0],
                   [0,0,1]])

    R = R1 @ R2 @ R3
    coords = R @ np.array([x,y,z])
    return coords

# -------------------- ANIMAȚIE --------------------
def generate_animation(coords, asteroid_name):
    gif_path = get_gif_filename(asteroid_name)
    if os.path.exists(gif_path):
        return

    x, y, z = coords
    theta_e = np.linspace(0, 2*np.pi, 500)
    r_e = (1*(1-0.0167**2)) / (1 + 0.0167*np.cos(theta_e))
    x_e, y_e, z_e = r_e*np.cos(theta_e), r_e*np.sin(theta_e), np.zeros_like(theta_e)

    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(x, y, z, color="red", alpha=0.6, label="Asteroid orbit")
    ax.plot(x_e, y_e, z_e, color="blue", alpha=0.6, label="Earth orbit")
    ax.scatter(0, 0, 0, color="gold", s=400, label="Sun")

    asteroid_point, = ax.plot([], [], [], 'ro', markersize=6)
    earth_point, = ax.plot([], [], [], 'bo', markersize=10)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_zlim(-1, 1)
    ax.set_xlabel("X [AU]")
    ax.set_ylabel("Y [AU]")
    ax.set_zlabel("Z [AU]")
    ax.legend()

    def update(frame):
        asteroid_point.set_data([x[frame]], [y[frame]])
        asteroid_point.set_3d_properties([z[frame]])
        earth_point.set_data([x_e[frame]], [y_e[frame]])
        earth_point.set_3d_properties([z_e[frame]])
        return asteroid_point, earth_point

    ani = FuncAnimation(fig, update, frames=len(x), interval=20, blit=True)
    ani.save(gif_path, writer='pillow')
    plt.close(fig)

# -------------------- ENERGIE & HARTĂ --------------------
def impact_energy_megatons(diameter_km, density_kgm3, v_kms):
    D_m = diameter_km * 1000
    V = 4/3 * np.pi * (D_m/2)**3
    m = density_kgm3 * V
    E_J = 0.5 * m * (v_kms*1000)**2
    return E_J / 4.184e15

def generate_map(E_mt, R_km, impact_coords=(45.0, 25.0)):
    lat, lon = impact_coords
    m = folium.Map(location=[lat, lon], zoom_start=5)
    folium.Marker([lat, lon], popup="Impact site").add_to(m)

    # varianta 1: cercuri doar contur (nu se suprapun complet)
    folium.Circle(
        location=[lat, lon],
        radius=R_km * 1000,
        color='red',
        fill=False,
        weight=3,
        opacity=0.9,
        popup=f"Energie: {E_mt:.2f} Mt TNT\nRaza: {R_km:.2f} km"
    ).add_to(m)

    folium.Circle(
        location=[lat, lon],
        radius=R_km * 1300,
        color='orange',
        fill=False,
        weight=3,
        opacity=0.8,
        dash_array='6,6',
        popup=f"Energie: {E_mt:.2f} Mt TNT\nRaza: {R_km:.2f} km"
    ).add_to(m)

    folium.Circle(
        location=[lat, lon],
        radius=R_km * 1700,
        color='green',
        fill=False,
        weight=3,
        opacity=0.7,
        dash_array='3,8',
        popup=f"Energie: {E_mt:.2f} Mt TNT\nRaza: {R_km:.2f} km"
    ).add_to(m)

    # varianta 2 (opțional): dacă vrei să păstrezi fill dar să eviți overlay total,
    # poți plasa cercurile foarte ușor decalate (metri)
    def offset_latlon(lat, lon, dx_m, dy_m):
        dLat = dy_m / 111320.0
        dLon = dx_m / (40075000 * np.cos(np.radians(lat)) / 360.0)
        return lat + dLat, lon + dLon

    # ex: dacă preferi decalare, comentează varianta 1 şi foloseşte aceasta
    # r_m = R_km * 1000
    # folium.Circle(location=offset_latlon(lat, lon, 0, 0), radius=r_m, color='red', fill=True, fill_opacity=0.25).add_to(m)
    # folium.Circle(location=offset_latlon(lat, lon, r_m*0.08, 0), radius=r_m*1.3, color='orange', fill=True, fill_opacity=0.18).add_to(m)
    # folium.Circle(location=offset_latlon(lat, lon, -r_m*0.08, r_m*0.06), radius=r_m*1.7, color='green', fill=True, fill_opacity=0.15).add_to(m)

    # Layer control util (permite dezactivare/activare)
    folium.LayerControl(collapsed=False).add_to(m)

    m.save("static/impact_map.html")

# -------------------- ESTIMARE NOUA DISTANTA --------------------
def estimate_new_approach_distance(original_distance_km, mass_ship, speed_ship_kms):
    """
    O estimare simplificată: modificăm distanța proporțional cu energia navetei
    """
    E_ship = 0.5 * mass_ship * (speed_ship_kms*1000)**2  # J
    factor = 1 + E_ship / 1e15  # scala simplificată
    new_distance = original_distance_km * factor
    return new_distance

# -------------------- PAGINA PRINCIPALĂ --------------------
@app.route("/", methods=["GET", "POST"])
def simulare():
    asteroid_list = get_asteroid_list()
    asteroid_name = E_mt = R_km = gif_path = new_approach_km = None
    impact_coords = (45.0, 25.0)
    map_version = None
    asteroid_data = None

    if request.method == "POST":
        selected_id = request.form.get("asteroid_id")
        lat = request.form.get("lat")
        lon = request.form.get("lon")
        mass_ship = request.form.get("mass_ship")
        speed_ship = request.form.get("speed_ship")

        if lat and lon:
            impact_coords = (float(lat), float(lon))

        if selected_id:
            url = f"https://api.nasa.gov/neo/rest/v1/neo/{selected_id}?api_key={API_KEY}"
            asteroid = requests.get(url).json()

            # după ce primești 'asteroid' din API
            asteroid_name = asteroid.get('name')
            # extrage câmpurile folosite în template
            close = asteroid.get('close_approach_data', [{}])[0]
            d_min = asteroid['estimated_diameter']['kilometers']['estimated_diameter_min']
            d_max = asteroid['estimated_diameter']['kilometers']['estimated_diameter_max']
            diameter_km = round((d_min + d_max) / 2, 3)
            asteroid_data = {
                "name": asteroid.get('name'),
                "id": asteroid.get('id'),
                "diameter_km": diameter_km,
                "h": asteroid.get('absolute_magnitude_h'),
                "velocity_kms": close.get('relative_velocity', {}).get('kilometers_per_second'),
                "close_approach_date": close.get('close_approach_date'),
                "is_potentially_hazardous": asteroid.get('is_potentially_hazardous_asteroid', False)
            }

            coords = calculate_orbit(asteroid)
            generate_animation(coords, asteroid_name)

            density = 2500

            try:
                v_kms = float(asteroid['close_approach_data'][0]['relative_velocity']['kilometers_per_second'])
            except:
                v_kms = 20.0

            E_mt = impact_energy_megatons(diameter_km, density, v_kms)
            R_km = 5 * (E_mt)**(1/3)
            generate_map(E_mt, R_km, impact_coords)
            map_version = int(time.time())  # cache buster pentru iframe
            gif_path = get_gif_filename(asteroid_name)

            # --- Estimare simplificată noua distanță ---
            original_distance_km = 500000  # km, exemplu simplificat
            if mass_ship and speed_ship:
                new_approach_km = estimate_new_approach_distance(
                    original_distance_km,
                    float(mass_ship),
                    float(speed_ship)
                )

    return render_template("simulare.html",
                           asteroid_list=asteroid_list,
                           asteroid_name=asteroid_name,
                           asteroid_data=asteroid_data,
                           E_mt=E_mt,
                           R_km=R_km,
                           gif_path=gif_path,
                           new_approach_km=new_approach_km,
                           map_version=map_version)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
