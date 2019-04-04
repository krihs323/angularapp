import { Component, OnInit } from '@angular/core';
import { Coche} from './coche';
import {PeticionesService} from '../services/peticiones.service';

@Component({
  selector: 'coche',
  templateUrl: './coche.component.html',
  styleUrls: ['./coche.component.css'],
  providers: [PeticionesService]
})
export class CocheComponent implements OnInit {
  public coche: Coche;
  public coches:Array<Coche>;
  public productos:any;
  constructor(
    private _peticionesService:PeticionesService
  ) {
    this.coche = new Coche("", "", "");
    this.coches = [
      new Coche("Seat panda", "120", "blanca"),
      new Coche("Ferrari", "1200", "rojo"),
    ];
    ///this.productos = "123";
    
  }

  ngOnInit() {
    
    console.log(this._peticionesService.getPrueba());

    this._peticionesService.getProductos().subscribe(
      result => {
           
          if(result.code != 200){
              console.warn(result);
              this.productos = result;
          }else{
              //this.productos = result.data;
          }

      },
      error => {
          console.log(<any>error);
      }
  );
    
  //console.warn(this.productos);
  
  }

  onSubmit(){
    this.coches.push(this.coche);
    this.coche = new Coche("", "", "");
  }

}
