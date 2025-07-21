document.addEventListener("DOMContentLoaded", function () {
  
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "/styles/navbar.css";
  document.head.appendChild(link);


const navbar = `
  <div class="navbar">
    <div class="logo"><a href="#">SES</a></div>
    <ul class="links">
      <li><a href="/index.html">Inicio</a></li>
      <li><a href="/empleados.html">Empleados</a></li>
      <li><a href="/clientes.html">Clientes</a></li>
      <li class="dropdown">
        <a href="/citas.html">Citas</a>
        <ul class="dropdown-menu">
          <li><a href="">Registrar cita</a></li>
          <li><a href="">Ver citas agendadas</a></li>
        </ul>
      </li>
      <li><a href="/inventario.html">Inventario</a></li>
    </ul>
    <button class="boton-elegante">LogOut</button>
  </div>`;

  document.body.insertAdjacentHTML("afterbegin", navbar);

});
