from coremod import overload

from core.system.terraform import PlaceUndergroundRegionTilesDelayedAction
from siege import game, InventoryItem
from siege.world import World

from core.monster.boss import spreadOre
from core.helper import sendMessage
from core.system.server import ServerHandler


@overload
def handleBossDefeat(realm, entity):
    for player in realm.players:
        ServerHandler.addToInventoryOrDrop(player, InventoryItem(game.content.get("way_shard")))
    sendMessage('general', 'System', 'TravelFromBossRealm', realm=realm)

    world = World.get()
    dataKey = 'lastDefeat{}'.format(entity.name)
    isFirstTime = dataKey not in world.data
    world.data[dataKey] = world.time.days.get()
    if 'defeated_bosses' not in player.data:
        player.data['defeated_bosses'] = {}
    contentName = entity.content.getName()
    if contentName not in player.data['defeated_bosses']:
        player.data['defeated_bosses'][contentName] = True

    if isFirstTime:
        bossDefeats = world.data.get('bossDefeats', 0) + 1
        world.data['bossDefeats'] = bossDefeats
    for player in realm.players:
        game.events['boss_defeated'].invoke(player, world)

    if isFirstTime:
        # Always drop Remna Core
        realm.dropped.create(InventoryItem('remna_core'), entity.getPosition())

        if bossDefeats == 1:
            world.remnaLevel = 1
            world.remnaLevel = 3
        elif bossDefeats == 2:
            # Spread Adamantite in main realm
            spreadOre(world, 'adamantite')
        elif bossDefeats == 3:
            # Spawn corium
            world.remnaLevel = 2
            spreadOre(world, 'corium')
        elif bossDefeats == 4:
            spreadOre(world, 'osmium', 'mithril', 'titanium', 'orichalcum', 'draconium', 'cobalt', 'uranium')
