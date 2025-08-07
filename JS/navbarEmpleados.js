document.addEventListener("DOMContentLoaded", function () {
  
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/styles/navbar.css";
  document.head.appendChild(link);


const navbar = `
  <div class="navbar">
    <div class="logo"><a href="/index.html">SES</a></div>
    <ul class="links">
      <li><a href="/index.html">Inicio</a></li>
      <li class="dropdown">
        <a href="">Empleado</a>
        <ul class="dropdown-menu">
          <li><a href="/asistencia.html">Registrar hora de entrada</a></li>
          <li><a href="/verAsistencia.html">Ver las asistencias</a></li>
        </ul>
      </li>
      <li><a href="/ReportesIncidentes.html">Reporte Incidentes</a></li>
      <li><a href="/verHorasExtras.html">Ver mis Horas extras</a></li>
    </ul>
    <a class="boton-elegante" href="/login.html">LogOut</a>
  </div>`;

  document.body.insertAdjacentHTML("afterbegin", navbar);

});