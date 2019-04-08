import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'plantilla',
  templateUrl: './plantilla.component.html',
  styleUrls: ['./plantilla.component.css']
})
export class PlantillaComponent implements OnInit {
  public titulo;
  public administrador;

  constructor() {
      this.titulo = 'Plantillas ngTemplate en angular';
      this.administrador = true;
   }

  ngOnInit() {
  }

  cambiar(valor) {
    this.administrador = valor;
  }

}
