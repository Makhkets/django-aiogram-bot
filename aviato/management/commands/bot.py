from django.core.management.base import BaseCommand
from .main import *

class Command(BaseCommand):
    help = "Telegram Bot"
    
    def handle(self, *args, **options):
        b = executor.start_polling(dp, skip_updates=True)