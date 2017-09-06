# LAB 4: APIs
## AleRSS

**El nombre de nuestro proyecto es una concatenacion de nuestros nombres y e
tipo de feed RSS.**

### La primera impresión
Partimos del ejemplo (*pastebin*) que dejó Cristian, a partir de ahí agregamos
cosas hasta que el **AleRSS** comenzó a andar solo con la autenticacion a traves
de github. Luego tuvimos que refactorizar el Auth para soportar mas proveedores
(clase SignIn). Nos entretuvimos mucho tiempo jugando con HTML, JavaScrip y
jQuery, por lo que cambiamos muchas cosas y esperamos no haber escrito mucho
codigo feo (tampoco sabemos como deberia lucir).

### El autenticador
Creamos instacias de `OAuth` y de `login_manager` acá porque estan totalmente
relacionadas con el manejo de sesiones.

Seguimos a medias el ejemplo de Miguel Grinberg (ver *Inspiracion*), porque
notamos que todos los `login()` y `callback()` eran casi iguales y diferian muy
poco. Por lo que decidimos hacer una implementacion general para todos los
proveedores, y que cada clase hija seteara los parametros que necesite.

Implementamos la clase **SignIn** con los metodos `login()`, `callback()` y
`get_provider()` para usarlos desde *runserver.py* independientemente del proveedor.

Por cada proveedor definimos una clase que hereda de `SignIn` y configuramos
`oauth` con los parametros necesarios para cada uno.

Los `remote_app` de `oauth` en general requieren una `consumer_key` y
`consumer_secret` que las conseguimos en las webs de desarrolladores de cada
proveedor. Ademas `request_token_params` especifica parametros extra, en la
mayoria de los casos es necesario, `scope : email` es para solicitar el email
del usuario. Los demas parametros requeridos los encontramos en la documentacion
de cada proveedor y en un repositorio con ejemplos en github (ver *Inspiracion*).

Siguiendo los ejemplos definimos los `tokengetter()`, y si un usuario quiere
ingresar a una pagina a la cual no tiene permisos, levantamos un abort con el
codigo de error 404.


### Corre server corre
Ya con una interfaz para el login de usuarios, en *runserver.py* controlamos las
peticiones de los usuarios. Ademas aca inicializamos la base de datos.

Usamos decoradores para *vincular* funciones con una solicitud al servidor,
para exigir que el usuario deba estar logueado, y definir una funcion especial
para capturar el error 404 y mostrar una pagina personalizada.

Algunas funciones necesitan el decorador `login_required` para proteger la
privacidad de los usuarios y para los que no estan registrados no puedan leer
feeds. Ademas tenemos metodos para crear, eliminar y mostrar feed.

Los metodos `login()`, `callback()` y `logout()` estan inspiradas en el tutorial
de Miguel Grinberg, pero difieren bastante.


### El sencillo
En *app.py* creamos la aplicacion flask, la configuramos a travez del archivo
setting previamente importado y definimos la base de datos.


### Los intactos
Setting y models no se tocaron.


### Cosas ramdom
No nos gusto el boton de eliminar y lo cambiamos por una cruz. Cambiamos el
`logut` y el `home` por iconos para que no dependa del idioma.

Al trabajar con javascript, al principio cuando el usuario hacia clic en el
boton `new feed` se hacia un `get` al servidor y devolviamos una pedazo de html
que iba a ser rendereado por javascript del lado del cliente. Pero si el
usuario ingresaba a la direccion `http://localhost:5000/new_feed` se mostraba
ese pedazo de html. Por lo que decidimos meter el html de *new_feed.html*
dentro de *index.html*, y con javascript ocultar todo lo del **index** y
mostrar las cosas del **new_feed**.

Tuvimos problemas cuando el usuario ingresa un nuevo feed valido y teniamos que
"actualizar" el **index**. Por lo que decidimos simplemente recargar la pagina
haciendo una redireccion.

Siguiendo con lo de javascript, decidimos enviar un json con un parametro
`status` que indica si el pedido fue exitoso o no (eliminar o agregar un feed).

Para los proveedores que no nos brindan el email del usuario, el parametro
`email` de la clase hija de `SignIn` es una string vacio para que no intente
sacar el email del token.

Tuvimos un problema con el login con `bitbucket`. Solicitamos el email, pero en
el token no está.

Para que un usuario logueado no pueda ver los feeds de otro usuario, al
realizar la busqueda en la base de datos, tambien comparamos el id del usuario.

Para que todos los **IDs** de los usuarios de todos los proveedores difieran,
decidimos guardar los `id` como `"<nobre_proveedor>$<id_usuario>"`

Linkedin es especial. Tuvimos una funcion extra que extraimos de un ejemplo
(ver *Inspiracion*) porque no podiamos extraer los datos del usuario.


### Ahora somos del club DEVs
Para crear las APIs de Github, Github, Dropbox, Linkedin y Bitbucket, nos
registramos como desarrolladores en respectivas paginas. Tuvimos bastantes
problemas en hacerlo andar por las URIs, los callbacks, las direcciones autorizadas, etc.


### Tambien somos miembros de testers
Testeamos lo mas que pudimos la interfaz, haciendo mas de dos clics a todo
(literalmente) y no encontramos bugs.


### Inspiracion
~~Copypastear todo el codigo que encontramos en stackoverflow, en github y en
la documentacion oficial.~~

Nos guiamos bastante con este [tutorial](http://blog.miguelgrinberg.com/post/oauth-authentication-with-flask)
para resolver el login.

Tambien parte del login fue sacado de este [repositorio](https://github.com/lepture/flask-oauthlib/tree/master/example)

Muchas respuestas vinieron del [MegaTutorial](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
tambien de **Miguel Grinberg**.

Para las demas APIs, leimos sus documentaciones oficiales.

Para javascript y html [usamos](http://www.w3schools.com/)

Para los iconos los encontramos [acá](http://fontawesome.io/icons/)

No hicimos los login con *Twitter*, *Facebook* ni *Instagram* porque pedian
numero de telefono.


### Justo lo necesario
No usamos mas librerias de las que propuso la catedra.
