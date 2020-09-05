def sort_firmware(firmwares):
    firmware_dict = {}
    for firmware in firmwares:
        for model in firmware.model_id.all():
            if firmware not in firmware_dict:
                firmware_dict[firmware] = {}
            if model.family_id not in firmware_dict[firmware]:
                firmware_dict[firmware][model.family_id] = []
            firmware_dict[firmware][model.family_id].append(model.model_number)
    return firmware_dict
