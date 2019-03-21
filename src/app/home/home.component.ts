import { Component, OnInit } from '@angular/core';
import { RopaService } from '../services/ropa.service';

@Component({
  selector: 'home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  providers:[RopaService]
})
export class HomeComponent implements OnInit {
  public titulo = 'Pagina Principal' ;
  public listado_ropa: Array<string>;
  public prenda_a_guardar: string;
  public fecha: any;
  public nombre: string;

  constructor(
    private _ropaService: RopaService
  ) { }

  ngOnInit() {
    this.listado_ropa = this._ropaService.getRopa();
    console.log(this._ropaService.prueba('camisa puma'));
    console.log(this.listado_ropa);
    this.fecha = new Date(2019, 2, 21);
    this.nombre = 'Cristia BOTINA';
  }

  guardarPrenda(){
    this._ropaService.addRopa(this.prenda_a_guardar);
    this.prenda_a_guardar = null;
  }

  eliminarPrenda(index:number){
    this._ropaService.deleteRopa(index);
  }

}
