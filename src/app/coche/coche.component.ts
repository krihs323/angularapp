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
  constructor(
    private _peticionesService:PeticionesService
  ) {
    this.coche = new Coche("", "", "");
    this.coches = [
      new Coche("Seat panda", "120", "blanca"),
      new Coche("Ferrari", "1200", "rojo"),
    ];
  }

  ngOnInit() {
    console.log(this._peticionesService.getPrueba());
    
  }

  onSubmit(){
    this.coches.push(this.coche);
    this.coche = new Coche("", "", "");
  }

}
