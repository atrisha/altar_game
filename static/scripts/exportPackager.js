

function exportSpriteGroupToJSON(group) {
    let spritesData = [];

    group.getChildren().forEach(sprite => {
        let spriteData = {
            x: sprite.x,
            y: sprite.y,
            textureKey: sprite.texture.key,
            frame: sprite.frame.name
        };
        spritesData.push(spriteData);
    });

    return JSON.stringify(spritesData, null, 4);
}
