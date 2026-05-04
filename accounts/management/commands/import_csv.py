import csv
import os
import time
import io
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.core.management.base import BaseCommand
from accounts.models import Machine_Logs, Machine

class CSVHandler(FileSystemEventHandler):
    def __init__(self, filepath, machine, stdout, style):
        self.filepath = os.path.abspath(filepath)
        self.machine = machine
        self.stdout = stdout
        self.style = style
        self.last_size = 0
        self.headers = []

        if os.path.exists(self.filepath):
            self.stdout.write(f"Initial check on {self.filepath}...")
            self.process_file()

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.filepath:
            self.process_file()

    def process_file(self):
        try:
            if not os.path.exists(self.filepath):
                return
                
            current_size = os.path.getsize(self.filepath)
            
            # File truncated or reset
            if current_size < self.last_size:
                self.last_size = 0
                self.stdout.write(self.style.WARNING("File size decreased. Resetting pointer..."))
            
            if current_size == self.last_size:
                return # No new data

            with open(self.filepath, mode='r', encoding='utf-8-sig') as f:
                if self.last_size == 0:
                    header_line = f.readline()
                    if header_line:
                        self.headers = next(csv.reader(io.StringIO(header_line)), [])
                        self.headers = [h.strip() for h in self.headers]
                    self.last_size = f.tell()

                f.seek(self.last_size)
                new_data = f.read()
                self.last_size = f.tell()

            if not new_data:
                return

            self.stdout.write(f"Detected newly added data. Processing rows...")
            reader = csv.reader(io.StringIO(new_data))
            success_count = 0
            
            for row_list in reader:
                if not row_list or all(not x.strip() for x in row_list):
                    continue
                
                row = dict(zip(self.headers, row_list))

                def parse_int(val):
                    if not val or val.strip() == '': return None
                    try: return int(float(val.strip()))
                    except ValueError: return None
                    
                def parse_float(val):
                    if not val or val.strip() == '': return None
                    try: return float(val.strip())
                    except ValueError: return None

                try:
                    Machine_Logs.objects.create(
                        machine=self.machine,
                        process_time_ms=parse_float(row.get('process_time_ms')),
                        caminput=parse_int(row.get('caminput')),
                        grayfilter=parse_int(row.get('grayfilter')),
                        shape01=parse_int(row.get('shape01')),
                        pos01=parse_int(row.get('pos01')),
                        label01=parse_int(row.get('label01')),
                        switch01=parse_int(row.get('switch01')),
                        posy01=parse_int(row.get('posy01')),
                        posy02=parse_int(row.get('posy02')),
                        posx01=parse_int(row.get('posx01')),
                        posx02=parse_int(row.get('posx02')),
                        shape02=parse_int(row.get('shape02')),
                        pos02=parse_int(row.get('pos02')),
                        switch02=parse_int(row.get('switch02')),
                        totalarea01=parse_int(row.get('totalarea01')),
                        numoflabels01=parse_int(row.get('numoflabels01')),
                        resultdisplay=parse_int(row.get('resultdisplay')),
                    )
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error on row: {row}. Error: {e}"))
            
            if success_count > 0:
                self.stdout.write(self.style.SUCCESS(f"Successfully imported {success_count} new log(s)."))
                
        except Exception as ex:
            self.stdout.write(self.style.ERROR(f"Error reading file: {ex}"))

class Command(BaseCommand):
    help = 'Watches a CSV file and imports newly added Machine_Logs data automatically.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file to watch.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        machine = Machine.objects.first()
        if not machine:
            self.stdout.write(self.style.ERROR('No Machine exists in the database. Please create one first or use seed_data.'))
            return

        abs_path = os.path.abspath(csv_file_path)
        watch_dir = os.path.dirname(abs_path)
        
        if not os.path.exists(watch_dir):
            self.stdout.write(self.style.ERROR(f'Directory "{watch_dir}" does not exist.'))
            return

        # Initialize handler
        event_handler = CSVHandler(abs_path, machine, self.stdout, self.style)
        
        # Setup watchdog observer
        observer = Observer()
        observer.schedule(event_handler, path=watch_dir, recursive=False)
        observer.start()
        
        self.stdout.write(self.style.SUCCESS(f"Watching for live changes in: {abs_path}"))
        self.stdout.write(self.style.SUCCESS("Press Ctrl+C to stop.\n"))
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()
