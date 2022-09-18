import logging
import random

from common.util import *
from common.types import ActionType, EntityType
from common.util import now
from config import Color, ShadowBossConfig
from entities.bullet import Bullet
from entities.shadow import Shadow

logger = logging.getLogger(__name__)


class ShadowBoss(Shadow):
    """Boss (a large shadow)."""
    HP_BAR_HEIGHT: int = 20
    HP_TEXT_HEIGHT_OFFSET: int = -40

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_hp = ShadowBossConfig.INITIAL_HP
        self.hp = self.initial_hp
        self.recent_action_started_at[ActionType.ANGRY] = now()
        self.health = 5000
        self.what_color_is_this = (255, 51, 153)
        self.getting_brith = ShadowBossConfig.ANGRY_INTERVAL_MS
        self.poping_babies = ShadowBossConfig.ANGRY_DURATION_MS
    def _update_action(self):
        
        if self.set_action(
            ActionType.ANGRY,
            duration_ms=self.poping_babies,
            interval_ms=self.getting_brith,
        ):
            self._get_angry()
        super()._update_action()

    def _get_angry(self):
        for _ in range(50):
            bullet_id = self.world.add_entity(
                EntityType.SHADOW_BULLET,
                self.rect.centerx + random.random() * self.rect.width / 2,
                self.rect.centery + random.random() * self.rect.height / 2,
            )

            bullet: Bullet = self.world.get_entity(bullet_id)
            bullet.move_random()
    def _take_damage(self, damage: int):
        self.hp -= damage
        self.start_hurt(duration_ms=ShadowBossConfig.HURT_DURATION_MS)

    def _handle_get_hit(self):
        bullet: Bullet
        for bullet in self.world.get_entities(EntityType.PLAYER_BULLET):
            if self.collide(bullet):

                # Unlike normal shadow vs. bullet interaction, the boss would absorb the bullet,
                # so we remove the bullet right here.
                self.world.remove_entity(bullet.id)

                self._take_damage(bullet.damage)

                if self.hp <= 2500:
                    self.health = 2500
                    self.what_color_is_this = (0,191,255)
                    self.getting_brith = self.getting_brith / 2
                if self.hp <= 1000:
                    self.getting_brith = self.getting_brith / 4
                    
                if self.hp <= 0:
                    self.die()
    def render(self, screen, *args, **kwargs) -> None:
        super().render(screen, *args, **kwargs)

        # Render boss HP
        if self.hp > 0:
            display_text(
                screen,
                f"{self.hp} / {self.health}",
                x=self.rect.x,
                y=self.rect.top + self.HP_TEXT_HEIGHT_OFFSET,
                color=Color.BOSS_HP_BAR,
            )

            draw_pct_bar(
                screen,
                fraction=self.hp / self.health,
                x=self.rect.x,
                y=self.rect.y - self.HP_BAR_HEIGHT,
                width=self.rect.width,
                height=self.HP_BAR_HEIGHT,
                color=self.what_color_is_this,
                margin=4,
            )