import { Component, OnInit } from '@angular/core';
import { Coche} from './coche';

@Component({
  selector: 'coche',
  templateUrl: './coche.component.html',
  styleUrls: ['./coche.component.css']
})
export class CocheComponent implements OnInit {
  public coche: Coche;
  constructor() {
    this.coche = new Coche("", "", "");
  }

  ngOnInit() {
  }

  onSubmit(){
    console.log(this.coche);
  }

}
