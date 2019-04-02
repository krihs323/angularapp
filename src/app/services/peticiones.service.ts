import {Injectable} from '@angular/core';
//import {Http, Response, Headers} from '@angular/http';
import { HttpClientModule } from '@angular/common/http';
import {map} from 'rxjs/operators';
import {Observable} from 'rxjs/Observable';

@Injectable()
export class PeticionesService{
  
    getPrueba(){
        //Uso de la libreria rxjs operators
        //.pipe(map(res => res.json())); 
        return "Hola mundodo desde el servicio peticiones!!";
    }

  
}
