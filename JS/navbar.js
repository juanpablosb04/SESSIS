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
      <li><a href="/empleados.html">Empleados</a></li>
      <li><a href="/clientes.html">Clientes</a></li>
      <li class="dropdown">
        <a href="">Citas</a>
        <ul class="dropdown-menu">
          <li><a href="/registrarCitas.html">Registrar cita</a></li>
          <li><a href="/verCitas.html">Ver citas agendadas</a></li>
        </ul>
      </li>
      <li><a href="/inventario.html">Inventario</a></li>
      <li class="dropdown">
        <a href="">Asistencia</a>
        <ul class="dropdown-menu">
          <li><a href="/asistencia.html">Registrar Asistencia</a></li>
          <li><a href="/verAsistencia.html">Ver las asistencias</a></li>
        </ul>
      </li>
      <li><a href="/reportes.html">Reportes</a></li>
    </ul>
    <button class="boton-elegante">LogOut</button>
    
  </div>`;

  document.body.insertAdjacentHTML("afterbegin", navbar);

});
