import {Component} from '@angular/core';
import {Empleado} from './empleado';


@Component({
  selector:'empleado',
  templateUrl: './empleado.component.html'
})

export class EmpleadoComponent{
  public empleado:Empleado;
  public trabajadores:Array<Empleado>;
  public trabajador_externo:boolean;
  public color:string;
  public color_seleccionado:string;

  constructor(){
    this.empleado = new Empleado('David Lopez',45,'Cocinero',true);
    this.trabajadores = [
       new Empleado('Manolo',20,'Cocinero',true),
       new Empleado('Ana',18,'Programador',false),
       new Empleado('Victor',45,'Mesero',true),
       new Empleado('Cristian Leandro Botina',29,'Analista',true),
    ];
    this.trabajador_externo = true;
    this.color = 'red';
    this.color_seleccionado = '#CCC';
  }

  ngOnInit(){
    console.log(this.empleado);
    console.log(this.trabajadores);
  }

  cambiarExterno(valor){
    this.trabajador_externo = valor;
  }


}
