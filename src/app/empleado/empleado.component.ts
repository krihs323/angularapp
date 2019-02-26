import { Component } from '@angular/core';
import { Empleado } from './empleado';

@Component ({
  selector: 'empleado',
  templateUrl: './empleado.component.html',
})
export class EmpleadoComponent{
  public titulo = 'Titulo del empleado ';
  public empleado:Empleado;
  public trabajadores:Array<Empleado>;

  ngOnInit(){
    this.empleado = new Empleado('Cristian Leandro',29, 'Analista', 'Si');
    this.trabajadores = [
      new Empleado('Francelina Caipe',54, 'Ama de casa', 'Si'),
      new Empleado('Jenifer Giraldo',34, 'Supervisora', 'Si')
    ];
    console.log(this.empleado);
  }
}
