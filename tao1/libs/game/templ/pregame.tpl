<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<title>Start game page</title>


        <!--<script src="/static/game/detector.js"></script>-->

		<script type="text/javascript" src="/static/app/jquery1.11.min.js"></script>
		<script type="text/javascript"          src="/static/app/bootstrap/js/bootstrap.min.js" ></script>
        <link rel="stylesheet" type="text/css" href="/static/app/bootstrap/css/bootstrap.min.css" />
        <link rel="stylesheet" type="text/css" href="/static/app/bootstrap/css/bootstrap-theme.min.css" />

        <link rel="stylesheet" href="/static/app/fa/css/font-awesome.min.css">

        <style type="text/css">
            .ctrl1 {
                border:1px solid #ccc;
                border-radius: 6px;
                margin: 3px;
                color:grey;
            }
        </style>

	</head>
	<body>


<div class="" style="width:1000px;">

    <div class="row" style="margin: 5px;">
		<div class="check_webgl col-xs-7" >
			<div class="">
				<h3>Проверка наличия WebGL в браузере.</h3>
                <p>К сожалению старые версии браузеров эту технологию не поддерживают, а internet explorer только начиная с 11 версии поддерживает WebGl. </p>
                <p>Как правило могут быть несколько случаев отсутствия поддержки это либо старая графическая карточка, либо устаревший браузер. </p>
			</div>
            <div class="webgl"></div>
            <div class="">
                <a href="https://support.google.com/chrome/answer/1220892?hl=ru">О подержке WebGl google-chrome</a><br/>
                <a href="http://askubuntu.com/questions/299345/how-to-enable-webgl-in-chrome-on-ubuntu">Как включить WebGl в google-chrome</a>
                <a href="http://superuser.com/questions/836832/how-can-i-enable-webgl-in-my-browser"> Как включить WebGl в google-chrome</a>
            </div>

            {{ room }}

            <div class="reg_game">
                <div style="width:200px; margin-top:20px;" class="btn btn-success  btn-block"> Start game</div>
    	    </div>

		</div>
        <script type="text/javascript">
        $(function(){
           $('.reg_game').on('click', 'div', function(){
               $.ajax({
                   type: "POST", dataType: "json", url: '/check_room',
                   data: {},
                   success: function (data) {
                       if (data.result == 'ok') {
                           window.location = '/game#'+data.room;
                       }
                   }
               });
           });
        });

        </script>

		<div class="regulate col-xs-5">
			<h3> Горячие клавиши для игры.</h3>

            <div class="row">
                <div class="col-xs-1"></div><div class="ctrl1 col-xs-2">&nbsp; W &nbsp;</div> &nbsp; - Вперед<br/><br/>
                <div class="ctrl1 col-xs-2">&nbsp; A &nbsp;</div>
                <div class="ctrl1 col-xs-2">&nbsp; D &nbsp;</div>  &nbsp; - Влево вправо<br/> <br/>
                <div class="col-xs-1"></div><div class="ctrl1 col-xs-2">&nbsp; S &nbsp;</div> &nbsp; - Назад
            </div>
            <hr/>
            <div class="row">
                <div class="col-xs-1"></div><div class="ctrl1 col-xs-2">&nbsp; <i class="fa fa-long-arrow-up"></i> &nbsp;</div> &nbsp; - Вперед<br/><br/>
                <div class="ctrl1 col-xs-2">&nbsp; <i class="fa fa-long-arrow-left"></i> &nbsp;</div>
                <div class="ctrl1 col-xs-2">&nbsp; <i class="fa fa-long-arrow-right"></i> &nbsp;</div>  &nbsp; - Влево вправо<br/> <br/>
                <div class="col-xs-1"></div><div class="ctrl1 col-xs-2">&nbsp; <i class="fa fa-long-arrow-down"></i> &nbsp;</div> &nbsp; - Назад
            </div>
            <hr/>
            <div class="row">
                <div class="col-xs-1"></div><div class="ctrl1 col-xs-5">&nbsp; SPACE (Пробел) &nbsp;</div> &nbsp; - Поднятие в верх
            </div>
            <hr/>
            <div class="row">
                <div class="col-xs-1"></div><div class="ctrl1 col-xs-6">&nbsp; Левая кнопка мышы &nbsp;</div> &nbsp; - Выстрел <br/><br/>
                <div class="col-xs-1"></div><div class="ctrl1 col-xs-6">&nbsp; Вращение мышы &nbsp;</div> &nbsp; - Вращение
            </div>
		</div>


	</div>



</div>




<script type="text/javascript">
    text = '<div class="jumbotron"> <div class="btn btn-success btn-xs"><i class="fa fa-check"></i></div> &nbsp Поздравляем, ваш браузер поддерживает технологию 3D WebGl.  </div>'
    text1 = '<div class="jumbotron"> <div class="btn btn-danger btn-xs"><i class="fa fa-remove"></i></div> &nbsp К сожалеию ваш браузер не поддерживает WebGl. ' +
            '<a href="https://support.google.com/chrome/answer/1220892?hl=ru">О подержке WebGl google-chrome</a><br/>  ' +
            '</div>'
    !!window.WebGLRenderingContext ? $('.webgl').append(text) : $('.webgl').append(text1);


</script>

	</body>
</html>


{#   1) setup ->    #}