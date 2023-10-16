

    var config = {
        type: Phaser.AUTO,
        width: 800,
        height: 800,
        physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 300 },
            debug: false
            }
        },
        scene: {
            preload: preload,
            create: create,
            update: update
        }
    };

    var game = new Phaser.Game(config);

    function preload ()
    {
        this.load.image('sky', 'static/phaser3-tutorial-src/assets/sky.png');
        this.load.image('ground', 'static/phaser3-tutorial-src/assets/platform.png');
        this.load.image('red_apple', 'static/phaser3-tutorial-src/assets/fruits/pngs/red_apple.png');
        this.load.image('banana', 'static/phaser3-tutorial-src/assets/fruits/pngs/bananas.png');
        this.load.image('bomb', 'static/phaser3-tutorial-src/assets/bomb.png');
        this.load.image('altar', 'static/phaser3-tutorial-src/assets/altar.png');
        this.load.spritesheet('dude', 
            'static/phaser3-tutorial-src/assets/dude.png',
            { frameWidth: 32, frameHeight: 48 }
        );
    }

    function collectStar (player, star)
    {   

        star.disableBody(true, true);
        score += 10;
        if (score==change_score)
        	{ 
				player.clearTint();
			}
        scoreText.setText('Score: ' + score);

         if (red_apples.countActive(true) === 0)
        {
            red_apples.children.iterate(function (child) {

                child.enableBody(true, child.x, 0, true, true);

            });

            var x = (player.x < 400) ? Phaser.Math.Between(400, 800) : Phaser.Math.Between(0, 400);

            var bomb = bombs.create(x, 16, 'bomb');
            //bomb.setBounce(1);
            bomb.setCollideWorldBounds(true);
            bomb.setVelocity(Phaser.Math.Between(-200, 200), 20);

        }
    }
    
    function eatAltarApple (player, apple)
    {   

        player.disableBody(true, true);
        
        // Enable the sprite's physics body
	    player.enableBody(true, player.x, player.y, true, true);
	    
	    // Set the sprite's alpha to 0 (make it fully transparent)
	    player.setAlpha(0);
	    
	    // Use a tween to fade the sprite in
	    this.tweens.add({
	        targets: player,
	        alpha: 1,  // Target alpha value (fully opaque)
	        duration: 3000,  // Duration in milliseconds
	        ease: 'Linear'  // Transition style
	    });
        
    }

    var score = 0;
    
    var scoreText;
    
    var change_score = 0

    function hitBomb (player, bomb)
    {
        this.physics.pause();

        player.setTint(0xff0000);

        player.anims.play('turn');

        gameOver = true;
        gameOverText.setVisible(true);

    }
    
    function hitBanana (player, banana)
    {	
		banana.disableBody(true, true);
		change_score = score;
        score = score - 20;
        scoreText.setText('Score: ' + score);

        player.setTint(0xffff00);

        player.anims.play('turn');
        
        if (bananas.countActive(true) === 0)
        {
            bananas.children.iterate(function (child) {

                child.enableBody(true, child.x, 0, true, true);

            });
         }

    }

    function create ()
    {
        var bg = this.add.image(400, 400, 'sky');
        var scaleX = this.cameras.main.width / bg.width;
	    var scaleY = this.cameras.main.height / bg.height;
	    var scale = Math.max(scaleX, scaleY);
	    bg.setScale(scale).setScrollFactor(0);
	    
	    
        platforms = this.physics.add.staticGroup();
		platforms.create(400, 768, 'ground').setScale(2).refreshBody();
		platforms.create(600, 600, 'ground');
        platforms.create(50, 450, 'ground');
        platforms.create(750, 420, 'ground');
        platforms.create(400, 300, 'ground').setScale(0.15,1).refreshBody();
        platforms.create(400, 300, 'ground').setScale(0.15,1).refreshBody();
        
        this.add.sprite(400, 250, 'altar').setScale(1.15);

        //player = this.physics.add.sprite(100, 450, 'dude');
        players = this.physics.add.group({
            key: 'dude',
            repeat: 1,
            setXY: { x: 100, y: 450, stepX: 100 }
        });
        players.children.iterate(function (child) {
            child.setBounce(0.2);
            child.setCollideWorldBounds(true);
        });
        //player.setBounce(0.2);
        //player.setCollideWorldBounds(true);

        red_apples = this.physics.add.group({
            key: 'red_apple',
            repeat: 4,
            setXY: { x: 12, y: 0, stepX: 70 }
        });
        
        var more_apples = this.physics.add.group({
            key: 'red_apple',
            repeat: 6,
            setXY: { x: 490, y: 0, stepX: 70 }
        });
        red_apples.addMultiple(more_apples.getChildren());
        
        red_apples.children.iterate(function (child) {
            child.setBounceY(Phaser.Math.FloatBetween(0.4, 0.8));
        });
        red_apples.children.iterate(sprite => sprite.setScale(0.15));
        
        altar_apple = this.physics.add.sprite(400, 272, 'red_apple').setScale(0.15);

        
        bananas = this.physics.add.group({
            key: 'banana',
            repeat: 0,
            setXY: { x: 315, y: 0, stepX: 70 }
        });
        bananas.children.iterate(function (child) {
            child.setBounceY(Phaser.Math.FloatBetween(0.4, 0.8));
        });
        bananas.children.iterate(sprite => sprite.setScale(0.15));
        

        bombs = this.physics.add.group();
		
		gameOverText = this.add.text(400, 300, 'Game Over', { fontSize: '64px', fill: '#ff0000' }).setOrigin(0.5).setVisible(false);



        

        this.physics.add.collider(players, platforms);
        this.physics.add.collider(red_apples, platforms);
        this.physics.add.collider(altar_apple, platforms);
        this.physics.add.collider(bombs, platforms);
        this.physics.add.collider(bananas, platforms);
        this.physics.add.collider(players, bombs, hitBomb, null, this);
        
        this.physics.add.collider(players, bananas, hitBanana, null, this);
		this.physics.add.overlap(players, red_apples, collectStar, null, this);
		this.physics.add.overlap(players, altar_apple, eatAltarApple, null, this);

        scoreText = this.add.text(16, 16, 'score: 0', { fontSize: '32px', fill: '#000' });

        this.anims.create({
            key: 'left',
            frames: this.anims.generateFrameNumbers('dude', { start: 0, end: 3 }),
            frameRate: 10,
            repeat: -1
        });

        this.anims.create({
            key: 'turn',
            frames: [ { key: 'dude', frame: 4 } ],
            frameRate: 20
        });

        this.anims.create({
            key: 'right',
            frames: this.anims.generateFrameNumbers('dude', { start: 5, end: 8 }),
            frameRate: 10,
            repeat: -1
        });

		// Use Phaser's timed events to send the sprite's state every 2 seconds (2000 milliseconds)
		this.time.addEvent({
		    delay: 1000,
		    callback: () => sendAndUpdateSpriteState(players.getChildren()[0]),
		    loop: true
		});

        cursors = this.input.keyboard.createCursorKeys();
        keyObj1 = this.input.keyboard.addKey('Q');
        keyObj2 = this.input.keyboard.addKey('W');

    }

    function update ()
    {	
    	
        
        red_apples.children.iterate(function(apple) {
		    if (!apple.active) {
		        apple.enableBody(true, Phaser.Math.FloatBetween(0, 800), 0, true, true);
		    }
		});

        
        if (keyObj1.isDown)
            {
                if (cursors.left.isDown)
                {
                    players.getChildren()[0].setVelocityX(-160);

                    players.getChildren()[0].anims.play('left', true);
                }
                else if (cursors.right.isDown)
                {
                    players.getChildren()[0].setVelocityX(160);

                    players.getChildren()[0].anims.play('right', true);
                }
                else
                {   
                    players.getChildren()[0].setVelocityX(0);

                    players.getChildren()[0].anims.play('turn');
                }
                if (cursors.up.isDown && players.getChildren()[0].body.touching.down)
                {
                    players.getChildren()[0].setVelocityY(-330);
                }
            }
        else if (keyObj2.isDown)
            {
                if (cursors.left.isDown)
                {
                    players.getChildren()[1].setVelocityX(-160);

                    players.getChildren()[1].anims.play('left', true);
                }
                else if (cursors.right.isDown)
                {
                    players.getChildren()[1].setVelocityX(160);

                    players.getChildren()[1].anims.play('right', true);
                }
                else
                {   
                    players.getChildren()[1].setVelocityX(0);

                    players.getChildren()[1].anims.play('turn');
                }

                if (cursors.up.isDown && players.getChildren()[1].body.touching.down)
                {
                    players.getChildren()[1].setVelocityY(-330);
                }
                else
                { 
                    console.log("here!!!");
                }
            }
    }
    
function sendAndUpdateSpriteState(sprite) {
    const spriteData = {
        x: sprite.x,
        y: sprite.y
        // Add any other properties you want to send
    };

    fetch('/send-sprite-state', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(spriteData)
    })
    .then(response => response.json())
    .then(data => {
        // Update the sprite based on the server's response
        //sprite.x = data.newX;
        //sprite.y = data.newY;
        ;
    });
}


    