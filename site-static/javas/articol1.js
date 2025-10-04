



function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
  }

  window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }


let calcScrollValue = () => {
    let scrollProgress = document.getElementById('progress');
    let progressValue = document.getElementById('progress-value');
    let pos = document.documentElement.scrollTop;
    let calcHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    let scrollValue = Math.round((pos * 100)/calcHeight);
    console.log(pos);

    if(pos > 100)
    {
        scrollProgress.style.display = "grid";
    }
        else
    {
        scrollProgress.style.display = "none";
    }
    scrollProgress.addEventListener("click", () => {
        document.documentElement.scrollTop = 0;
    })

    scrollProgress.style.background = `conic-gradient(#DD6B4D ${scrollValue}%, #d7d7d7 ${scrollValue}%)`;

};


window.onscroll = calcScrollValue;
window.onload = calcScrollValue;

let butonApasat = document.getElementById('meet');

butonApasat.addEventListener("click", () => {
    window.location.href = "../html/team.html";
});

let logoApasat = document.getElementById('logodiv');

logoApasat.addEventListener("click", () => {
    window.location.href = "../html/index.html";
});