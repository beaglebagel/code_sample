"""
Simple command to_recipient clear django cache.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clear Django cache'

    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cache has been cleared!'))