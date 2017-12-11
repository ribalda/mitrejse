ARDUINO_PATH = $(CURDIR)/../arduino-1.8.5
SKETCHBOOK = $(CURDIR)/../sketchbook
ESPTOOL = $(SKETCHBOOK)/hardware/esp8266com/esp8266/tools/esptool/esptool
ESPTOOLPY = $(CURDIR)/../esptool-2.1/esptool.py
SKETCH = $(notdir $(CURDIR)).ino
TARGET_DIR = $(CURDIR)/build-esp8266
MONITOR_PORT ?= /dev/ttyUSB0
TARGET_IP ?= 192.168.1.169

all:
	@ mkdir -p $(TARGET_DIR)

	$(ARDUINO_PATH)/arduino-builder -compile -logger=machine \
	-hardware "$(ARDUINO_PATH)/hardware" \
	-hardware "$(SKETCHBOOK)/hardware" \
	-tools "$(ARDUINO_PATH)/tools-builder" \
	-tools "$(ARDUINO_PATH)/hardware/tools/avr" \
	-built-in-libraries "$(ARDUINO_PATH)/libraries" \
	-libraries "$(SKETCHBOOK)/libraries" \
	-fqbn=esp8266com:esp8266:nodemcuv2:CpuFrequency=80,UploadSpeed=115200,FlashSize=4M3M \
	-ide-version=10805 \
	-build-path "$(TARGET_DIR)" \
	-warnings=none \
	-prefs=build.warn_data_percentage=75 \
	-prefs=runtime.tools.xtensa-lx106-elf-gcc.path=$(SKETCHBOOK)/hardware/esp8266com/esp8266/tools/xtensa-lx106-elf \
	-prefs=runtime.tools.esptool.path=$(SKETCHBOOK)/hardware/esp8266com/esp8266/tools/esptool \
	-verbose "$(SKETCH)"

flash:
	$(ESPTOOL) -v -cd nodemcu -cb 115200 -cp $(MONITOR_PORT) -ca 0x00000 -cf $(TARGET_DIR)/$(SKETCH).bin

flash.py:
	$(ESPTOOLPY) --port $(MONITOR_PORT) write_flash -fm dio 0x00000 $(TARGET_DIR)/$(SKETCH).bin

flash.ota:
	curl -F "image=@$(TARGET_DIR)/$(SKETCH).bin" $(TARGET_IP)/update

install: all flash.py

install.ota: all flash.ota

clean:
	rm -rf $(TARGET_DIR)

monitor:
	screen $(MONITOR_PORT) 115200

monitor.py:
	miniterm.py $(MONITOR_PORT) 115200
