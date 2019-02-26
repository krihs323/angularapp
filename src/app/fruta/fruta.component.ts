import { Component } from '@angular/core';

@Component ({
  selector: 'fruta',
  templateUrl: './fruta.component.html',
})
export class FrutaComponent{
  public titulo = 'Titulo de la fruta ';
  public frutas = 'Mango, Papaya ';
  public trabajos:Array<any>=['Carpintero',144,'Fontanero'];
  public nombre:string;
  public edad:number;
  public mayorDeEdad:boolean;

  constructor(){
    this.nombre = 'cristian';
    this.edad = 29;
    this.mayorDeEdad = true;
  }

  ngOnInit(){
    this.holaMundo();
  }

  holaMundo() {
      console.log("Helo Word of word!!");
  }
}
