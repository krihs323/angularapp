import { Component, OnInit } from '@angular/core';
import { Coche} from './coche';

@Component({
  selector: 'coche',
  templateUrl: './coche.component.html',
  styleUrls: ['./coche.component.css']
})
export class CocheComponent implements OnInit {
  public coche: Coche;
  public coches:Array<Coche>;
  constructor() {
    this.coche = new Coche("", "", "");
    this.coches = [
      new Coche("Seat panda", "120", "blanca"),
      new Coche("Ferrari", "1200", "rojo"),
    ];
  }

  ngOnInit() {
  }

  onSubmit(){
    this.coches.push(this.coche);
    this.coche = new Coche("", "", "");
  }

}
