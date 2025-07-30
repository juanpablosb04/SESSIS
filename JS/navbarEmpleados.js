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
      <li><a href="/empleados.html">Marcar horario</a></li>
      <li><a href="/clientes.html">Reporte Incidentes</a></li>
      <li><a href="/inventario.html">Horas extras</a></li>
    </ul>
    <button class="boton-elegante">LogOut</button>
  </div>`;

  document.body.insertAdjacentHTML("afterbegin", navbar);

});