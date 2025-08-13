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
          <li><a href="/Administrador/empleados.html">Registrar y consultar Empleados</a></li>
          <li><a href="/Administrador/horasExtras.html">Registrar Horas Extras</a></li>
           <li><a href="/Administrador/asistencia.html">Asistencia de empleados</a></li>
        </ul>
      </li>
      <li><a href="/Administrador/clientes.html">Clientes</a></li>
      <li class="dropdown">
        <a href="">Citas</a>
        <ul class="dropdown-menu">
          <li><a href="/Administrador/registrarCitas.html">Registrar cita</a></li>
          <li><a href="/Administrador/consultarCitas.html">Ver citas agendadas</a></li>
        </ul>
      </li>
      <li><a href="/Administrador/inventario.html">Inventario</a></li>
      <li><a href="/Administrador/reportesGenerales.html">Reportes</a></li>
      <li><a href="/Administrador/usuarios.html">Usuarios</a></li>
    </ul>
    <a class="boton-elegante" href="/login.html">LogOut</a>

    
  </div>`;

  document.body.insertAdjacentHTML("afterbegin", navbar);

});

      