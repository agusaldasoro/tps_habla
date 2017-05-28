Los pasos que seguimos para llevar a cabo el Trabajo Practico fueron:

1) Leer la entrada y definir si ibamos a tener que modificar la prosodia o no, en caso de que fuera una interrogacion.
2) En base a la entrada dividir la frase en difonos (agregandole los caracteres - de inicio y fin).
3) Copiar de los difonos grabados cada uno de los necesarios en el orden que los necesitamos en una carpeta temporal.
4) Crear el script de praat en 'concatenate.praat' que concatena los archivos wav que almacenan los difonos necesarios.
5) Ejecutar el script de praat que crea el archivo .wav con la frase deseada.
6) Si se debe modificar la prosodia:
	- Se calcula el pitch track del audio con el script 'extract-pitch-track.praat'.
	- Se crea un nuevo archivo con el pitch track modificado.
	- Mediante el script 'replace-pitch-track' se modifica el pitch track del audio.
7) Eliminar los archivos temporales creados.



Para modificar la prosodia de modo que suene una pregunta, intentamos imitar una curva ascendente al final de la frase sumandole una funcion lineal.
Para ello, experimentamos con distintos valores de x e y. Siendo:
	x: el porcentaje de la frase final a la cual se le modificara el pitch track
	y: la cantidad de que se le suma en cada punto del pitch calculado

Luego de probar con distintos valores, definimos que se modifica el 20% final de la frase, sumandole en cada punto 20 en su pitch track.
