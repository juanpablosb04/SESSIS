document.addEventListener("DOMContentLoaded", function () {
  
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/static/navbar.css";
  document.head.appendChild(link);


const navbar = `
  <div class="navbar">
    <div class="logo"><a href="/">SES</a></div>
    <ul class="links">
      <li><a href="/inicio">Inicio</a></li>
      <li class="dropdown">
        <a href="#">Empleado</a>
        <ul class="dropdown-menu">
          <li><a href="/empleados">Registrar y consultar Empleados</a></li>
          <li><a href="/horasExtras">Registrar Horas Extras</a></li>
          <li><a href="/asistencia">Asistencia de empleados</a></li>
        </ul>
      </li>
      <li><a href="/clientes">Clientes</a></li>
      <li class="dropdown">
        <a href="#">Citas</a>
        <ul class="dropdown-menu">
          <li><a href="/registrarCitas">Registrar cita</a></li>
          <li><a href="/consultarCitas">Ver citas agendadas</a></li>
        </ul>
      </li>
      <li><a href="/inventario">Inventario</a></li>
      <li><a href="/reportes">Reportes</a></li>
      <li><a href="/usuarios">Usuarios</a></li>
    </ul>
    <a class="boton-elegante" href="/logout">LogOut</a>
  </div>`;


  document.body.insertAdjacentHTML("afterbegin", navbar);

});

      