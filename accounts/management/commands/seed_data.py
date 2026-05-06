import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import (
    Profile,
    Machine,
    Machine_Logs,
    Machine_Logs_Images,
)

# ---------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------

FIRST_NAMES = [
    "Minh","Hung","Lan","Hoa","Tuan","Anh","Long","Phuc",
    "Dung","Ngoc","Thao","Linh","Khoa","Binh","Cuong",
]

LAST_NAMES = [
    "Nguyen","Tran","Le","Pham","Hoang","Huynh","Phan",
    "Vu","Dang","Bui","Do","Ho","Ngo","Duong","Ly",
]

MACHINE_PREFIXES = [
    "CNC","Robot","Conveyor","Press","Lathe","Mill",
    "Drill","Grinder","Welder","Cutter","Packager","Sorter",
]

BIO_SAMPLES = [
    "Production line engineer with 5 years experience.",
    "Industrial machinery maintenance specialist.",
    "Production shift supervisor.",
    "CNC technician with Fanuc certification.",
    "Automation engineer working with PLC systems.",
]

LOCATIONS = [
    "Ha Noi","Ho Chi Minh City","Da Nang",
    "Binh Duong","Dong Nai","Hai Phong",
]



# ---------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------

class Command(BaseCommand):

    help = "Seed sample data"

    def add_arguments(self, parser):
        parser.add_argument("--flush",action="store_true")
        parser.add_argument("--users",type=int,default=5)
        parser.add_argument("--machines",type=int,default=6)
        parser.add_argument("--logs",type=int,default=10)

    # -------------------------------------------------------------

    def _flush_data(self):
        self.stdout.write("Flushing data...")

        Machine_Logs_Images.objects.all().delete()
        Machine_Logs.objects.all().delete()
        Machine.objects.all().delete()
        Profile.objects.all().delete()

        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Database cleaned"))

    # -------------------------------------------------------------

    def _create_admin(self):
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@machinemanagement.vn",
                password="Admin@123456",
            )
            Profile.objects.create(
                user=admin,
                bio="System administrator",
                location="Ha Noi",
            )
            self.stdout.write(
                self.style.SUCCESS("Admin created: admin / Admin@123456")
            )

    # -------------------------------------------------------------

    def _create_users(self,num_users):
        users=[]
        for i in range(1,num_users+1):
            username=f"user_{i:02d}"
            user=User.objects.create_user(
                username=username,
                email=f"{username}@factory.vn",
                password="User@123456",
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
            )
            Profile.objects.create(
                user=user,
                bio=random.choice(BIO_SAMPLES),
                location=random.choice(LOCATIONS),
            )
            users.append(user)
        return users

    # -------------------------------------------------------------

    def _create_machines(self,users,machines_per_user):
        machines=[]
        for user in users:
            for _ in range(machines_per_user):
                name=f"{random.choice(MACHINE_PREFIXES)}-{random.randint(100,999)}"
                machine=Machine.objects.create(
                    user=user,
                    name=name,
                    description="Industrial machine"
                )
                machines.append(machine)
        return machines

    # -------------------------------------------------------------

    def _create_logs(self,machines,logs_per_machine):
        log_objects=[]
        now=timezone.now()
        start_time=now-timedelta(hours=9)
        start_time=start_time.replace(
            minute=0,
            second=0,
            microsecond=0
        )

        for machine in machines:
            for i in range(logs_per_machine):
                # -----------------------------------------
                # CREATED TIME DISTRIBUTED BY HOUR
                # -----------------------------------------
                created_time=start_time+timedelta(
                    hours=i%9,
                    minutes=random.randint(0,59),
                    seconds=random.randint(0,59),
                )

                # Pass / Fail status determination
                is_pass = random.random() < 0.7
                
                status = 'OK'
                error_cols = ['misaligned_component', 'missing_component', 'missing_label', 'missing_pin', 'wrong_polarity']
                row_data = {col: 0 for col in error_cols}
                row_data.update({f"{col}_Conf": round(random.uniform(0.8, 1.0), 2) for col in error_cols})
                
                if not is_pass:
                    status = 'NG'
                    num_faults = random.randint(1, min(3, len(error_cols)))
                    fault_cols = random.sample(error_cols, num_faults)
                    for col in fault_cols:
                        row_data[col] = random.randint(1, 3)
                        row_data[f"{col}_Conf"] = round(random.uniform(0.9, 0.99), 2)
                        
                datetime_str = created_time.strftime("%Y%m%d_%H%M%S")

                log_objects.append(
                    Machine_Logs(
                        machine=machine,
                        processing_time=random.uniform(50.0, 100.0),
                        Status=status,
                        created=created_time,
                        **row_data
                    )
                )

        Machine_Logs.objects.bulk_create(log_objects)

        # -------------------------------------------------
        logs=Machine_Logs.objects.order_by("-id")[:len(log_objects)]
        images=[]
        for log in logs:
            if random.random()>0.5:
                images.append(
                    Machine_Logs_Images(
                        machine_log=log,
                        image_url="machine_logs_images/sample_image.jpg"
                    )
                )

        Machine_Logs_Images.objects.bulk_create(images)
        return log_objects

    # -------------------------------------------------------------

    def handle(self,*args,**options):
        if options["flush"]:
            self._flush_data()

        self._create_admin()
        users=self._create_users(options["users"])
        machines=self._create_machines(users, options["machines"])
        logs=self._create_logs(machines, options["logs"])

        self.stdout.write(
            self.style.SUCCESS(
                f"""
SEED COMPLETED

Users: {User.objects.count()}
Machines: {Machine.objects.count()}
Logs: {Machine_Logs.objects.count()}

Login:
admin / Admin@123456
user_01 / User@123456
"""
            )
        )