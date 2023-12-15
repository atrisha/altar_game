iter_per_calc = 500
async function walkPath(scene,sprite,path,speed) {
    //console.log(sprite)
    //console.log(sprite.x,sprite.y)
    //console.log(sprite.current_path)
    var action = { Xv: 0, Yv: 0 };
    
    currentPathIndex = sprite.currentPathIndex
    
    const targetPoint = path[currentPathIndex];
    if (targetPoint === 'undefined'){
        console.log(path,currentPathIndex)
    }
    const finalPoint = path[path.length-1];
    try{
        distance = Phaser.Math.Distance.Between(sprite.x, sprite.y, targetPoint.x, targetPoint.y);
    } catch(error){
        console.error('error_msg',path,currentPathIndex,targetPoint);
        throw error
    }
        const finaldistance = Phaser.Math.Distance.Between(sprite.x, sprite.y, finalPoint.x, finalPoint.y);
    
    if (Math.abs(finaldistance) < 32) {
        currentPathIndex++;
        delete sprite.current_path;
        delete sprite.currentPathIndex;
        sprite.body.reset(finalPoint.x, finalPoint.y);
    } else {
        
        
        const angle = Phaser.Math.Angle.Between(sprite.x, sprite.y, targetPoint.x, targetPoint.y);
        if (sprite.x < targetPoint.x) {
            action.Xv = 1
        } else if (sprite.x > targetPoint.x) {
            action.Xv = -1
        } else {
            action.Xv = 0
        }

        if (sprite.y < targetPoint.y) {
            action.Yv = -1
        } else if (sprite.y > targetPoint.y) {
            action.Yv = 1
        } else {
            action.Yv = 0
        }

        
        
        prevVelocity = sprite.body.velocity.clone();
        // Stop any previous movement from the last frame
        //sprite.body.setVelocity(0);
        if (action.Xv < 0) {
          sprite.body.setVelocityX(-speed);
        } else if (action.Xv > 0) {
          sprite.body.setVelocityX(speed);
        }
        
        // Vertical movement
        if (action.Yv > 0) {
          sprite.body.setVelocityY(-speed);
        } else if (action.Yv < 0) {
          sprite.body.setVelocityY(speed);
        }
        // Normalize and scale the velocity so that sprite can't move faster along a diagonal
        sprite.body.velocity.normalize().scale(speed);
        
        //anglemove = scene.physics.moveTo(sprite,targetPoint.x, targetPoint.y,speed)
        sprite.curr_target_pt = targetPoint
        sprite.currentPathIndex++

        var newAngles = Phaser.Math.RadToDeg(angle)
        if (sprite.body.speed > 0)
        {
            if(newAngles <= -45 && newAngles >= -135) {
                sprite.anims.play('misa-back', true)
            } else if (newAngles <= 45 && newAngles >= -45) {
                sprite.anims.play('misa-right-walk', true)
            } else if (newAngles <= 135 && newAngles >= 45) {
                sprite.anims.play('misa-front', true)
            } else if (newAngles <= 225 && newAngles >= 135) {
                sprite.anims.play('misa-left-walk', true)
            }
            
            
            
            if (distance < 16)
            {
                sprite.anims.pause()
                sprite.body.reset(targetPoint.x, targetPoint.y);                
            }
        }       
          
    }
    
}


function getLayerIndices(layer) {
    let indicesArray = [];
    const tileWidth = layer.tilemap.tileWidth;
    const tileHeight = layer.tilemap.tileHeight;
    const layerWidthInTiles = layer.width / tileWidth;
    const layerHeightInTiles = layer.height / tileHeight;
    for (let x = 0; x < layerWidthInTiles; x++) {
        const row = [];
        for (let y = 0; y < layerHeightInTiles; y++) {
            const tile = layer.getTileAt(x, y);
            //indicesArray[x][y] = tile ? 1 : 0; // Using -1 for empty tiles
            row.push(tile ? 1 : 0);
        }
        indicesArray.push(row);
    }
    return indicesArray;
}

function handleExplore(options){
<<<<<<< HEAD
    let { easystar, easystar_alt, player, spawnlayer_arr, walk_arr, visit_locs, game } = options;
=======
    let { easystar, easystar_alt, player, spawnlayer_arr, walk_arr, game } = options;
>>>>>>> 8d0ed88f26d73f75e887e62ed0ab21090ae60a04
    let easystar_obj;
    if (typeof player.current_path !== 'undefined' && player.currentPathIndex < player.current_path.length){
        console.log(player.name+' will walk '+player.currentPathIndex+'/'+player.current_path.length);
        walkPath(scene,player,player.current_path,game.config.rps*32);
        
    } else {
<<<<<<< HEAD
        if (visit_locs == null){
            spwans = game.spawnSpriteAtRandomTile();
            to_visit = {x: spwans.worldX/32, y: spwans.worldY/32} 
        } else {
            to_visit = visit_locs
        }
        
=======
        spwans = game.spawnSpriteAtRandomTile();
>>>>>>> 8d0ed88f26d73f75e887e62ed0ab21090ae60a04
        

        if (spawnlayer_arr[Math.floor(player.x/32)][Math.floor(player.y/32)] == 1){
            easystar_obj = easystar
        } else {
            easystar_obj = easystar_alt
        }
<<<<<<< HEAD
        easystar_obj.findPath(Math.floor(player.y/32), Math.floor(player.x/32), Math.floor(to_visit.y), Math.floor(to_visit.x), function( path ) {
=======
        easystar_obj.findPath(Math.floor(player.y/32), Math.floor(player.x/32), Math.floor(spwans.worldY/32), Math.floor(spwans.worldX/32), function( path ) {
>>>>>>> 8d0ed88f26d73f75e887e62ed0ab21090ae60a04
        console.log(player.name+' new path generated ');
        if (path === null) {
            console.log('no path');
            console.log(walk_arr);
            console.log(Math.floor(player.x/32),Math.floor(player.y/32),player.name);
            console.log(spawnlayer_arr[Math.floor(player.x/32)][Math.floor(player.y/32)]);
            console.log(walk_arr[Math.floor(player.x/32)][Math.floor(player.y/32)]);
            console.log('target',Math.floor(spwans.worldX/32),Math.floor(spwans.worldY/32))
<<<<<<< HEAD
            game.reset_player(player)
=======
            throw new Error('no path error')
>>>>>>> 8d0ed88f26d73f75e887e62ed0ab21090ae60a04
        } else {
            if (path.length>0) {
                world_path = path.map(point => ({x: point.y*32+16, y: point.x*32+16}));
                player.current_path = world_path;
                player.currentPathIndex = 1
                walkPath(scene,player,world_path,game.config.rps*32);
                //game.drawSimplePolyline(world_path);
            }
            
        }
        });
        easystar_obj.setIterationsPerCalculation(iter_per_calc);
        easystar_obj.calculate()
    }
    
}

function handleEatObject(options){
   let {easystar,easystar_alt,player,spawnlayer_arr,walk_arr,game,object_sprite} = options;
   let easystar_obj;
   if (spawnlayer_arr[Math.floor(player.x/32)][Math.floor(player.y/32)] == 1 && spawnlayer_arr[Math.floor(object_sprite[0].x)][Math.floor(object_sprite[0].y)] == 1){
        easystar_obj = easystar;
    } else {
        easystar_obj = easystar_alt;
    }
    try {
        easystar_obj.findPath(Math.floor(player.y/32), Math.floor(player.x/32), Math.floor(object_sprite[0].y), Math.floor(object_sprite[0].x), function( path ) {
            if (path === null) {
                console.log('no path');
                console.log(walk_arr);
                console.log(Math.floor(player.x/32),Math.floor(player.y/32),player.name);
                console.log(spawnlayer_arr[Math.floor(player.x/32)][Math.floor(player.y/32)],spawnlayer_arr[Math.floor(object_sprite[0].x)][Math.floor(object_sprite[0].y)]);
                console.log(walk_arr[Math.floor(player.x/32)][Math.floor(player.y/32)],walk_arr[Math.floor(object_sprite[0].x)][Math.floor(object_sprite[0].y)]);
                console.log('target',Math.floor(object_sprite[0].x),Math.floor(object_sprite[0].y))
                console.log(path)
                throw new Error('no path error')
            } else {
                if (path.length>0) {
                    world_path = path.map(point => ({x: point.y*32+16, y: point.x*32+16}));
                    player.current_path = world_path;
                    player.currentPathIndex = 1
                    walkPath(scene,player,world_path,game.config.rps*32);
                    //game.drawSimplePolyline(world_path);
                }
            }
        });
    } catch(error) {
        console.error(Math.floor(player.y/32), Math.floor(player.x/32), Math.floor(object_sprite[0].y), Math.floor(object_sprite[0].x))
        throw error
    }
    easystar_obj.setIterationsPerCalculation(iter_per_calc);
    easystar_obj.calculate()
}

function handleVisitObject(options){
    let {easystar,easystar_alt,player,spawnlayer_arr,walk_arr,game,object_sprite} = options;
    let easystar_obj;
    if (spawnlayer_arr[Math.floor(player.x/32)][Math.floor(player.y/32)] == 1 && spawnlayer_arr[Math.floor(object_sprite[0].x)][Math.floor(object_sprite[0].y)] == 1){
         easystar_obj = easystar;
     } else {
         easystar_obj = easystar_alt;
     }
     try {
         easystar_obj.findPath(Math.floor(player.y/32), Math.floor(player.x/32), Math.floor(object_sprite[0].y), Math.floor(object_sprite[0].x), function( path ) {
             if (path === null) {
                 console.log('no path');
                 console.log(walk_arr);
                 console.log(Math.floor(player.x/32),Math.floor(player.y/32),player.name);
                 console.log(spawnlayer_arr[Math.floor(player.x/32)][Math.floor(player.y/32)],spawnlayer_arr[Math.floor(object_sprite[0].x)][Math.floor(object_sprite[0].y)]);
                 console.log(walk_arr[Math.floor(player.x/32)][Math.floor(player.y/32)],walk_arr[Math.floor(object_sprite[0].x)][Math.floor(object_sprite[0].y)]);
                 console.log('target',Math.floor(object_sprite[0].x),Math.floor(object_sprite[0].y))
                 console.log(path)
                 throw new Error('no path error')
             } else {
                 if (path.length>0) {
                     world_path = path.map(point => ({x: point.y*32+16, y: point.x*32+16}));
                     player.current_path = world_path;
                     player.currentPathIndex = 1
                     walkPath(scene,player,world_path,game.config.rps*32);
                     //game.drawSimplePolyline(world_path);
                 }
             }
         });
     } catch(error) {
         console.error(Math.floor(player.y/32), Math.floor(player.x/32), Math.floor(object_sprite[0].y), Math.floor(object_sprite[0].x))
         throw error
     }
     easystar_obj.setIterationsPerCalculation(iter_per_calc);
     easystar_obj.calculate()
 }

function handleAvoidObject(options){
    let {easystar,easystar_alt,player,spawnlayer_arr,walk_arr,game,object_sprite} = options;
    let easystar_obj;
    if (typeof player.current_path !== 'undefined' && player.currentPathIndex < player.current_path.length){
        console.log(player.name+' will walk '+player.currentPathIndex+'/'+player.current_path.length);
        walkPath(scene,player,player.current_path,game.config.rps*32);
        
    } else {
        spwans = game.spawnSpriteAtRandomTile();
        

        if (spawnlayer_arr[Math.floor(player.x/32)][Math.floor(player.y/32)] == 1){
            easystar_obj = easystar
        } else {
            easystar_obj = easystar_alt
        }
        object_sprite.forEach((object) => {
            easystar_obj.setAdditionalPointCost(object.y, object.x, 100);
        });
        easystar_obj.findPath(Math.floor(player.y/32), Math.floor(player.x/32), Math.floor(spwans.worldY/32), Math.floor(spwans.worldX/32), function( path ) {
        console.log(player.name+' new path generated ');
        if (path === null) {
            console.log('no path');
            console.log(walk_arr);
            console.log(Math.floor(player.x/32),Math.floor(player.y/32),player.name);
            console.log(spawnlayer_arr[Math.floor(player.x/32)][Math.floor(player.y/32)]);
            console.log(walk_arr[Math.floor(player.x/32)][Math.floor(player.y/32)]);
            //console.log('target',Math.floor(spwans.worldX/32),Math.floor(spwans.worldY/32))
<<<<<<< HEAD
            game.reset_player(player)
=======
            throw new Error('no path error')
>>>>>>> 8d0ed88f26d73f75e887e62ed0ab21090ae60a04
        } else {
            if (path.length>0) {
                world_path = path.map(point => ({x: point.y*32+16, y: point.x*32+16}));
                player.current_path = world_path;
                player.currentPathIndex = 1
                walkPath(scene,player,world_path,game.config.rps*32);
                //game.drawSimplePolyline(world_path);
            }
            
        }
        });
        easystar_obj.setIterationsPerCalculation(iter_per_calc);
        easystar_obj.calculate()
    }
 }
