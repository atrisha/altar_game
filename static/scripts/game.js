


let player;
var score_1 = 0;
var scoreText_1;
var change_score_1 = 0

var score_2 = 0;
var scoreText_2;
var change_score_2 = 0

class MainScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MainScene' });
    }

    preload() {
        // Runs once, loads up assets like images and audio
        this.load.image("tiles", "/static/assets/tilesets/tuxmon-sample-32px-extruded.png");
        this.load.image("tiles_pipoya", "/static/assets/tilesets/pipo-map001.png");
        this.load.tilemapTiledJSON("map", "/static/assets/tilemaps/tuxemon-town.json");
        /*
        this.load.spritesheet('dude', 
                  'assets/dude.png',
                  { frameWidth: 32, frameHeight: 48 }
              );
              */
        this.load.atlas("atlas", "/static/assets/atlas/atlas.png", "/static/assets/atlas/atlas.json");
        this.load.image('banana', '/static/assets/bananas.png');
        this.load.image('red_apple', '/static/assets/red_apple.png');
        this.load.image('star', '/static/assets/star.png');
      
      }
      
      
      
      
      spawnSpriteAtRandomTile() {
          
          const randomIndex = Phaser.Math.Between(0, spawnable_tiles.length - 1);
          const randomTile = spawnable_tiles[randomIndex];
          
          // Convert tile coordinates to world coordinates
          const worldX = randomTile.x/40 * config.width;
          const worldY = randomTile.y/40 * config.height;
      
          // Spawn the sprite at the calculated position
          return {
              worldX: worldX,  // Some value for worldX
              worldY: worldY   // Some value for worldY
          };
      }
      
      handlePlayerInteraction(sprite1, sprite2) {
        
          if (sprite1.poisoned && !sprite1.marked) {
            score_1 = score_1 - 20;
            scoreText_1.setText('Score'+': ' + score_1);
            sprite1.marked = true
            punishment_stars.getChildren()[0].enableBody(true, sprite1.x, sprite1.y, true, true);
            punishment_stars.getChildren()[0].setAlpha(1);
            
          }    
          if (sprite2.poisoned && !sprite2.marked) {
            score_1 = score_1 - 20;
            scoreText_1.setText('Score'+': ' + score_1);
            sprite2.marked = true
            punishment_stars.getChildren()[1].enableBody(true, sprite2.x, sprite2.y, true, true);
            punishment_stars.getChildren()[1].setAlpha(1);
            
          } 
          
          /*
          this.tweens.add({
                  targets: player,
                  alpha: 0,  // Target alpha value (fully opaque)
                  duration: 1000,  // Duration in milliseconds
                  ease: 'Linear'  // Transition style
              });
          */
            //punishment_star.disableBody(true,true)
      
      }
      
      
      hitBanana (player, banana)
          {	
            banana.disableBody(true, true);
            /*    
            change_score_1 = score_1;
            score_1 = score_1 - 20;
            scoreText_1.setText('Score'+': ' + score_1);
            */
      
            player.setTint(0x00ff00);
            player.poisoned = true
            
            
              
              if (bananas.countActive(true) === 0)
              {
                  bananas.children.iterate(function (child) {
                    spawns = spawnSpriteAtRandomTile() 
                    console.log(spawns)
                    child.enableBody(true, spawns.worldX, spawns.worldY, true, true);
      
                  });
               }
      
          }
      
      eatAltarBanana (apple, player)
          { 
            player.clearTint();
            player.poisoned = false
            player.marked = false
            apple.disableBody(true, true);
              
              // Enable the sprite's physics body
            //player.enableBody(true, 1076, 194, true, true);
            apple.enableBody(true, apple.x, apple.y, true, true);
              
              // Set the sprite's alpha to 0 (make it fully transparent)
              apple.setAlpha(0);
              
              // Use a tween to fade the sprite in
              this.tweens.add({
                  targets: apple,
                  alpha: 1,  // Target alpha value (fully opaque)
                  duration: 3000,  // Duration in milliseconds
                  ease: 'Linear'  // Transition style
              });
              
          }    
      collectStar (player, star)
          {   
      
              star.disableBody(true, true);
              
              score_1 += 10;
              scoreText_1.setText('Score' +': ' + score_1);
                  
               if (red_apples.countActive(true) === 0)
              {   
                  
                  
                  red_apples.children.iterate(function (child) {
                    spawns = spawnSpriteAtRandomTile() 
                    console.log(spawns)
                    child.enableBody(true, spawns.worldX, spawns.worldY, true, true);
      
                  });
                }
          }
      
      
      getCollision(obj_arr) {
        let obj = obj_arr.find(item => item.name === 'collides');
        let value = obj ? obj.value : false;
        return value;
      }
      
      getSpawnable(obj_arr) {
        
        let obj = obj_arr.find(item => item.name === 'can_spawn');
        let value = obj ? obj.value : false;
        return value;
      }
      
      spawnable_tiles = []
      
      getAvailableTiles(map) {
          let availableTiles = [];
          layerName = 'spawn_layer'
          const layer = map.getLayer(layerName).data;
      
          for (let y = 0; y < layer.length; y++) {
              for (let x = 0; x < layer[y].length; x++) {
                  let tile = layer[y][x];
                  
                  // Check if the tile meets your criteria
                  if (tile.index !== -1) {
                      availableTiles.push({ x: x, y: y });
                  }
              }
          }
      
          spawnable_tiles = availableTiles;
      }
      
      
      create() {
        
        map = this.make.tilemap({ key: "map" });
        // Parameters are the name you gave the tileset in Tiled and then the key of the tileset image in
        // Phaser's cache (i.e. the name you used in preload)
        const tileset = map.addTilesetImage("tuxmon-sample-32px-extruded", "tiles");
        const tileset_pipoya = map.addTilesetImage("pipoya", "tiles_pipoya");
        const tileWidth = 32; // Or whatever your tile width is
        const tileHeight = 32; // Or whatever your tile height is
        const scaleFactorX = config.width / (map.width * tileWidth);
        const scaleFactorY = config.height / (map.height * tileHeight);
      
        // belowLayer = map.createStaticLayer("Below Player", tileset, 0, 0).setScale(scaleFactorX, scaleFactorY);
         //worldLayer = map.createStaticLayer("World", tileset, 0, 0).setScale(scaleFactorX, scaleFactorY);
         //aboveLayer = map.createStaticLayer("Above Player", tileset, 0, 0).setScale(scaleFactorX, scaleFactorY);
         //spawnLayer = map.createStaticLayer("spawn_layer", tileset, 0, 0).setScale(scaleFactorX, scaleFactorY);
        belowLayer = map.createStaticLayer("Below Player", tileset, 0, 0);
        worldLayer = map.createStaticLayer("World", tileset, 0, 0);
        aboveLayer = map.createStaticLayer("Above Player", tileset, 0, 0);
        spawnLayer = map.createStaticLayer("spawn_layer", tileset, 0, 0)
        pipoyaLayer = map.createStaticLayer("pipoya_1", tileset_pipoya, 0, 0)
        
        
        aboveLayer.setDepth(10);
        const spawnPoint = map.findObject("Objects", obj => obj.name === "Spawn Point");
        console.log('spawn point',spawnPoint)
        getAvailableTiles(map)
        console.log(spawnable_tiles)
        /*
        players = this.physics.add.group({
                  key: 'dude',
                  repeat: 0,
                  setXY: { x: 400, y: 325 }
              });*/
        
        cursors = this.input.keyboard.createCursorKeys();
        players = this.physics.add.group();
        for (let i = 0; i < 2; i++) {
          spwans = spawnSpriteAtRandomTile()
          console.log(spwans)
          players.create(spwans.worldX, spwans.worldY, "atlas", "misa-front");
        }
        player_names = ['player_1','player_2']
        let idx = 0
        players.getChildren().forEach(sprite => {
          sprite.name = player_names[idx++]
          sprite.marked = false
        });
      
        /*
        player = this.physics.add
          .sprite(spawnPoint.x,spawnPoint.y, "atlas", "misa-front")
          .setSize(30, 40)
          .setOffset(0, 24);
        */
        this.physics.add.collider(players, worldLayer);
        const anims = this.anims;
        anims.create({
          key: "misa-left-walk",
          frames: anims.generateFrameNames("atlas", { prefix: "misa-left-walk.", start: 0, end: 3, zeroPad: 3 }),
          frameRate: 10,
          repeat: -1
        });
        anims.create({
          key: "misa-right-walk",
          frames: anims.generateFrameNames("atlas", { prefix: "misa-right-walk.", start: 0, end: 3, zeroPad: 3 }),
          frameRate: 10,
          repeat: -1
        });
        anims.create({
          key: "misa-front-walk",
          frames: anims.generateFrameNames("atlas", { prefix: "misa-front-walk.", start: 0, end: 3, zeroPad: 3 }),
          frameRate: 10,
          repeat: -1
        });
        anims.create({
          key: "misa-back-walk",
          frames: anims.generateFrameNames("atlas", { prefix: "misa-back-walk.", start: 0, end: 3, zeroPad: 3 }),
          frameRate: 10,
          repeat: -1
        });
        
        worldLayer.setCollisionByExclusion([-1], true);
        navMesh = this.navMeshPlugin.buildMeshFromTilemap("mesh", map, [worldLayer]);
        
        this.physics.add.collider(players, worldLayer);
        //player.body.collideWorldBounds=true;
      
        
      
        
        red_apples = this.physics.add.group();
        for (let i = 0; i < 2; i++) {
          spwans = spawnSpriteAtRandomTile()
          console.log(spwans)
          red_apples.create(spwans.worldX, spwans.worldY, 'red_apple');
        }
        red_apples.children.iterate(sprite => sprite.setScale(0.15));
      
        bananas = this.physics.add.group();
        for (let i = 0; i < 2; i++) {
          spwans = spawnSpriteAtRandomTile()
          bananas.create(spwans.worldX, spwans.worldY, 'banana');
        }
        red_apples.children.iterate(sprite => sprite.setScale(0.15));
        bananas.children.iterate(sprite => sprite.setScale(0.15));
      
        this.physics.add.overlap(players, red_apples, collectStar, null, this);
        this.physics.add.overlap(players, bananas, hitBanana, null, this);
      
        altar_banana = this.physics.add.sprite(1076, 194, 'banana').setScale(0.25);
        this.physics.add.overlap(players, altar_banana, eatAltarBanana, null, this);
        bananas.children.iterate(sprite => sprite.setScale(0.12));
      
        this.physics.add.overlap(players, players, handlePlayerInteraction, null, this);
        punishment_stars = this.physics.add.group();
        for (let i = 0; i < 2; i++) {
          punishment_stars.create(1076, 194, 'star');
        }
        punishment_stars.children.iterate(sprite => sprite.disableBody(true,true));
        
      
        scoreText_1 = this.add.text(16, 30, 'Score: 0', { fontSize: '28px', fill: "#000000",backgroundColor: "#ffffff" });
        coreText_1 = this.add.text(16, 60, 'Press Q/W (and arrows) to move player', { fontSize: '28px', fill: "#000000",backgroundColor: "#ffffff" });
        keyObj1 = this.input.keyboard.addKey('Q');
        keyObj2 = this.input.keyboard.addKey('W');
        
        
        this.time.addEvent({
                  delay: 1000/config.rps,
                  callback: () => stateDispatch(),
                  loop: true
              });
        
        /*
        const debugGraphics = this.add.graphics().setAlpha(0.7);
        worldLayer.renderDebug(debugGraphics, {
          tileColor: null,                 // Color of non-colliding tiles
          collidingTileColor: new Phaser.Display.Color(243, 134, 48, 255),  // Color of colliding tiles, in this case, we set it to orange
          faceColor: new Phaser.Display.Color(40, 39, 37, 255)  // Color of colliding face edges
        });
        */
        
      
      
      }
      
      
      update(time, delta) {
        /*
        var prevVelocity = 0
            if (keyObj1.isDown) {
              var player = players.getChildren()[0] 
              const speed = 175;
              prevVelocity = player.body.velocity.clone();
      
              // Stop any previous movement from the last frame
              player.body.setVelocity(0);
      
              // Horizontal movement
              if (cursors.left.isDown && keyObj1.isDown) {
                player.body.setVelocityX(-speed);
              } else if (cursors.right.isDown && keyObj1.isDown) {
                player.body.setVelocityX(speed);
              }
      
              // Vertical movement
              if (cursors.up.isDown && keyObj1.isDown) {
                player.body.setVelocityY(-speed);
              } else if (cursors.down.isDown && keyObj1.isDown) {
                player.body.setVelocityY(speed);
              }
      
              // Normalize and scale the velocity so that player can't move faster along a diagonal
              player.body.velocity.normalize().scale(speed);
      
              // Update the animation last and give left/right animations precedence over up/down animations
              if (cursors.left.isDown && keyObj1.isDown) {
                player.anims.play("misa-left-walk", true);
              } else if (cursors.right.isDown && keyObj1.isDown) {
                player.anims.play("misa-right-walk", true);
              } else if (cursors.up.isDown && keyObj1.isDown) {
                player.anims.play("misa-back-walk", true);
              } else if (cursors.down.isDown && keyObj1.isDown) {
                player.anims.play("misa-front-walk", true);
              } else {
                player.anims.stop();
                player.body.setVelocity(0);
                // If we were moving, pick and idle frame to use
                if (prevVelocity.x < 0) player.setTexture("atlas", "misa-left");
                else if (prevVelocity.x > 0) player.setTexture("atlas", "misa-right");
                else if (prevVelocity.y < 0) player.setTexture("atlas", "misa-back");
                else if (prevVelocity.y > 0) player.setTexture("atlas", "misa-front");
              }
        } else if (keyObj2.isDown){
              var player = players.getChildren()[1] 
              const speed = 175;
              prevVelocity = player.body.velocity.clone();
      
              // Stop any previous movement from the last frame
              player.body.setVelocity(0);
      
              // Horizontal movement
              if (cursors.left.isDown && keyObj2.isDown) {
                player.body.setVelocityX(-speed);
              } else if (cursors.right.isDown && keyObj2.isDown) {
                player.body.setVelocityX(speed);
              }
      
              // Vertical movement
              if (cursors.up.isDown && keyObj2.isDown) {
                player.body.setVelocityY(-speed);
              } else if (cursors.down.isDown && keyObj2.isDown) {
                player.body.setVelocityY(speed);
              }
      
              // Normalize and scale the velocity so that player can't move faster along a diagonal
              player.body.velocity.normalize().scale(speed);
      
              // Update the animation last and give left/right animations precedence over up/down animations
              if (cursors.left.isDown && keyObj2.isDown) {
                player.anims.play("misa-left-walk", true);
              } else if (cursors.right.isDown && keyObj2.isDown) {
                player.anims.play("misa-right-walk", true);
              } else if (cursors.up.isDown && keyObj2.isDown) {
                player.anims.play("misa-back-walk", true);
              } else if (cursors.down.isDown && keyObj2.isDown) {
                player.anims.play("misa-front-walk", true);
              } else {
                player.anims.stop();
                player.body.setVelocity(0);
                // If we were moving, pick and idle frame to use
                if (prevVelocity.x < 0) player.setTexture("atlas", "misa-left");
                else if (prevVelocity.x > 0) player.setTexture("atlas", "misa-right");
                else if (prevVelocity.y < 0) player.setTexture("atlas", "misa-back");
                else if (prevVelocity.y > 0) player.setTexture("atlas", "misa-front");
              
                }
          
      
        }
        if (keyObj1.isUp){
          var player = players.getChildren()[0]
          player.anims.stop();
          player.body.setVelocity(0)
        }
        if (keyObj2.isUp){
          var player = players.getChildren()[1]
          player.anims.stop();
          player.body.setVelocity(0)
        }
        
        players.getChildren().forEach((sprite,idx) => {
          if (sprite.marked){
            
            punishment_stars.getChildren()[idx].x=sprite.x
            punishment_stars.getChildren()[idx].y=sprite.y
          } else{
            punishment_stars.getChildren()[idx].disableBody(true,true)
          }
        });
      
       */
       
      }
      
      backendHandler(player_actions){
        console.log(player_actions)
        for (const [index,action] of player_actions.entries()) {
            var player = players.getChildren()[index] 
            const speed = 175;
            prevVelocity = player.body.velocity.clone();
            // Stop any previous movement from the last frame
            player.body.setVelocity(0);
            if (action.Xv < 0) {
              player.body.setVelocityX(-speed);
            } else if (action.Xv > 0) {
              player.body.setVelocityX(speed);
            }
      
            // Vertical movement
            if (action.Yv > 0) {
              player.body.setVelocityY(-speed);
            } else if (action.Yv < 0) {
              player.body.setVelocityY(speed);
            }
            // Normalize and scale the velocity so that player can't move faster along a diagonal
            player.body.velocity.normalize().scale(speed);
      
            if (action.Xv < 0) {
              player.anims.play("misa-left-walk", true);
            } else if (action.Xv > 0) {
              player.anims.play("misa-right-walk", true);
            } else if (action.Yv > 0) {
              player.anims.play("misa-back-walk", true);
            } else if (action.Yv < 0) {
              player.anims.play("misa-front-walk", true);
            } else {
              player.anims.stop();
              player.body.setVelocity(0);
              // If we were moving, pick and idle frame to use
              if (prevVelocity.x < 0) player.setTexture("atlas", "misa-left");
              else if (prevVelocity.x > 0) player.setTexture("atlas", "misa-right");
              else if (prevVelocity.y < 0) player.setTexture("atlas", "misa-back");
              else if (prevVelocity.y > 0) player.setTexture("atlas", "misa-front");
            
              }
        }
        return true
      }
      
      resizeSnapshot(originalImage, width, height) {
          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(originalImage, 0, 0, width, height);
          const resizedImage = new Image();
          resizedImage.src = canvas.toDataURL();
          return resizedImage;
      }
      
      
      data_req = async (formData) => {
        const response = await fetch('/state-dispatch', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: formData});
        return resp_json = await response.json();
        
      }
      last_dispatch_complete = true
      stateDispatch() {
        if (last_dispatch_complete) {
          /*
          game.renderer.snapshot(imageBlob_full =>
          {   
              
            //console.log(imageBlob_full)
            const imageBlob = resizeSnapshot(imageBlob_full, 80, 80);
            //console.log(imageBlob)
            const popup = window.open("", "Image Popup", "width=600,height=400");
        
            // Ensuring the popup was successfully created
            if (popup) {
                // Writing basic HTML structure to popup
                popup.document.write("<!DOCTYPE html><html><head><title>Image Popup</title></head><body></body></html>");
      
                // Appending the img element to the body of popup
                popup.document.body.appendChild(imageBlob);
            } else {
                alert("Popup blocked. Please allow popups for this website.");
            }
            //console.log('snap!');
            
            
          },type='image/jpeg',encoderOptions=0.1);
          */
          playerGroup_data = exportSpriteGroupToJSON(players);
          console.log('sent')
          const path = navMesh.findPath({ x: 288, y: 320 }, { x: 1056, y: 256 });
          console.log(path)
          last_dispatch_complete = false
          data_req(playerGroup_data).then(resp_json => {
            handled = backendHandler(resp_json.player_actions);
            last_dispatch_complete = handled
            //finalTexture.clear();
            //renderTexture_dynamic.clear();
            console.log('received')
          }).catch(error => {
            last_dispatch_complete = false
            console.error(error); // Handle any errors here
          });
          
          
          
          
          
          
      
        }
         
        
      
      

}
}


const config = {
    type: Phaser.AUTO, // Which renderer to use
    width: 1280, // Canvas width in pixels
    height: 1280, // Canvas height in pixels
    parent: "game-container", // ID of the DOM element to add the canvas to
    scene: MainScene,
    rps: 4,
    physics: {
      default: "arcade",
      arcade: {
        gravity: { y: 0 }, // Top down game, so no gravity
        debug: false
      }
    },
    plugins: {
           scene: [
               {
                   key: "PhaserNavMeshPlugin", // Key to store the plugin class under in cache
                   plugin: PhaserNavMeshPlugin, // Class that constructs plugins
                   mapping: "navMeshPlugin", // Property mapping to use for the scene, e.g. this.navMeshPlugin
                   start: true
               }
           ]
       }
  };
  
const game = new Phaser.Game(config);