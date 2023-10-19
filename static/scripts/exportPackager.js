
function getSurroundingTilesInfo(player, layers) {
    const object_map = {
        'houses': {'ranges':['360-663']},
        'trees': {'list':[168,169,192,193]},
        'altar': {'list':[4,5,6,28,29,30,52,53,54]},
        'fountain': {'list':[272,273,274,296,297,298,320,321,322]}
    };

    function getObjectFromTileId(tileId) {
        for (const [objectName, tiles] of Object.entries(object_map)) {
            if ('ranges' in tiles) {
                for (const range of tiles.ranges) {
                    const [start, end] = range.split('-').map(Number);
                    if (tileId >= start && tileId <= end) {
                        return objectName;
                    }
                }
            } else if ('list' in tiles) {
                if (tiles.list.includes(tileId)) {
                    return objectName;
                }
            } 
        }
        return null;
    }

    let tilesInfo = {};
    
    layers.forEach((layer, layerIndex) => {
        for (let offsetX = -5; offsetX <= 5; offsetX++) {
            for (let offsetY = -5; offsetY <= 5; offsetY++) {
                const tile = layer.getTileAtWorldXY(player.x + offsetX * 32, player.y + offsetY * 32);
                if (tile) {
                    let objectName = getObjectFromTileId(tile.index);
                    objectName = objectName? objectName : 'immaterial';
                    if (!tilesInfo[objectName]) {
                        tilesInfo[objectName] = [];
                    }
                    tilesInfo[objectName].push({
                        tilePosition: {x: tile.x, y: tile.y},
                        layer: layerIndex
                    });
                    
                }
            }
        }
    });
    return tilesInfo;
}





function viewToArray(player, game_obj){
    let surroundingTilesInfo = getSurroundingTilesInfo(player, [game_obj.belowLayer, game_obj.worldLayer, game_obj.aboveLayer]);
    game_obj.red_apples.getChildren().forEach(sprite => {
        if (sprite.body.enable && Math.abs(sprite.x-player.x) < 32*5 && Math.abs(sprite.y-player.y)< 32*5){
            if (!surroundingTilesInfo['apple']) {
                surroundingTilesInfo['apple'] = [];
            }
            console.log(sprite)
            surroundingTilesInfo['apple'].push({
                tilePosition: {x: sprite.x/32, y: sprite.y/32},
                layer: -1
            });
        }
      });
      game_obj.bananas.getChildren().forEach(sprite => {
        if (sprite.body.enable && Math.abs(sprite.x-player.x) < 32*5 && Math.abs(sprite.y-player.y)< 32*5){
            if (!surroundingTilesInfo['banana']) {
                surroundingTilesInfo['banana'] = [];
            }
            surroundingTilesInfo['banana'].push({
                tilePosition: {x: sprite.x/32, y: sprite.y/32},
                layer: -1
            });
        }
      });
    return surroundingTilesInfo
}

function exportSpriteGroupToJSON(game_obj) {
    let group = game_obj.players
    let spritesData = [];

    group.getChildren().forEach(sprite => {
        let spriteData = {
            x: sprite.x,
            y: sprite.y,
            textureKey: sprite.texture.key,
            frame: sprite.frame.name,
            surroundingInfos: viewToArray(sprite, game_obj),
            poisoned: sprite.poisoned ? true : false

        };
        spritesData.push(spriteData);
    });

    return JSON.stringify(spritesData, null, 4);
}
