from google.cloud import compute_v1
import time
import json
from solana.keypair import Keypair

PROJECT_ID = "#######PROJECT_iD######"    
ZONE = "us-central1-a"               
IMAGE_FAMILY = "debian-11"         
IMAGE_PROJECT = "debian-cloud"       
INSTANCE_TYPE = "e2-micro"           
NUMBER_OF_INSTANCES = 10            

GITHUB_REPO = "https://github.com/Th0mmi3/auto_comment.git"
REPO_DIR = "/opt/repo"          
SCRIPT_TO_RUN = "commenter.py" 

def generate_wallet():
    keypair = Keypair.generate()
    wallet = {
        "public_key": str(keypair.public_key),
        "secret_key": list(keypair.secret_key)
    }
    return wallet

def load_startup_script(filepath):
    with open(filepath, "r") as f:
        script = f.read()
    script = script.format(REPO_DIR=REPO_DIR, GITHUB_REPO=GITHUB_REPO, SCRIPT_TO_RUN=SCRIPT_TO_RUN)
    return script

def create_instance(instance_name, wallet):
    instance_client = compute_v1.InstancesClient()

    image_client = compute_v1.ImagesClient()
    image_response = image_client.get_from_family(project=IMAGE_PROJECT, family=IMAGE_FAMILY)
    source_disk_image = image_response.self_link

    instance = compute_v1.Instance()
    instance.name = instance_name
    instance.machine_type = f"zones/{ZONE}/machineTypes/{INSTANCE_TYPE}"

    disk = compute_v1.AttachedDisk()
    disk.auto_delete = True
    disk.boot = True
    disk.initialize_params.source_image = source_disk_image
    disk.initialize_params.disk_size_gb = 10
    instance.disks = [disk]

    network_interface = compute_v1.NetworkInterface()
    network_interface.name = "global/networks/default"
    instance.network_interfaces = [network_interface]

    startup_script = load_startup_script("startup_script.sh")
    metadata_item = compute_v1.Items()
    metadata_item.key = "startup-script"
    metadata_item.value = startup_script

    metadata = compute_v1.Metadata()
    metadata.items = [metadata_item]
    instance.metadata = metadata

    operation = instance_client.insert(project=PROJECT_ID, zone=ZONE, instance_resource=instance)
    print(f"VM {instance_name} wordt aangemaakt met wallet {wallet['public_key']}...")
    wait_for_operation(operation)

def wait_for_operation(operation):
    """Wacht tot de instantie-aanmaakoperatie voltooid is."""
    operation_client = compute_v1.ZoneOperationsClient()
    print("Wachten op voltooiing van de operatie...", end="")
    while True:
        result = operation_client.get(project=PROJECT_ID, zone=ZONE, operation=operation.name)
        if result.status == compute_v1.Operation.Status.DONE:
            if result.error:
                print("\nEr is een fout opgetreden bij het maken van de instantie:")
                print(result.error)
            else:
                print(" Klaar.")
            break
        print(".", end="", flush=True)
        time.sleep(2)

def main():
    for i in range(NUMBER_OF_INSTANCES):
        instance_name = f"vps-{i+1}"
        wallet = generate_wallet() 
        create_instance(instance_name, wallet)

if __name__ == "__main__":
    main()
