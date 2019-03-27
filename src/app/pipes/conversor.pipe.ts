import {Pipe, PipeTransform} from "@angular/core";

@Pipe({ name: 'conversor' })

export class ConversorPipe implements PipeTransform{
    transform(value, por) {
        const valueOne = parseInt(value);
        const valueTwo = parseInt(por);

        const result = 'la multiplicacion: ' + valueOne + ' X ' + valueTwo + '=' + (valueOne * valueTwo);
        return result;
    }
}
