"use strict";
class Instrument {
    static baseSize = 375;
    #container;

    constructor(target) {
        this.#container = document.getElementById(target);
        // Rear box and front ring
        this.#container.innerHTML = '\
        <div class="instrument">\
          <img src="img/box.svg" class="box back"/>\
          <div class="specific"></div>\
          <img src="img/ring.svg" class="box"/>\
        </div>';
    }

    resize(size) {
        var element = this.#container.querySelector('div.instrument');
        element.style.width = size;
        element.style.height = size;
    }

    getInstrumentDiv() {
        return this.#container.querySelector('div.instrument div.specific');
    }

    // Show hide the rear box
    showBox(box) {
        var element = this.#container.querySelector('div.instrument img.box.back');
        if (box) {
            element.style.visibility = 'visible';
        }
        else {
            element.style.visibility = 'hidden';
        }
    }
};

class AirSpeed extends Instrument {
    static min = 0;
    static max = 160;
    #needle;

    constructor(target, size, showbox) {
        super(target);
        var innerInstrument = super.getInstrumentDiv();
        innerInstrument.className = "airspeed";
        innerInstrument.innerHTML = '\
        <img src="img/airspeed_back.svg" class="box"/>\
        <img src="img/needle.svg" class="needle box"/>';
        super.resize(size);
        super.showBox(showbox);

        // Get reference to moving element
        this.#needle = innerInstrument.querySelector('img.needle');

        this.setAirSpeed(0);
    }

    setAirSpeed(speed) {
        if (speed > AirSpeed.max) {
            speed = AirSpeed.max;
        } else if (speed < AirSpeed.min) {
            speed = AirSpeed.min;
        }
        var needlePos = 90 + speed * 2;
        this.#needle.style.transform = `rotate(${needlePos}deg)`;
    }
};

class Heading extends Instrument {
    #headingPointer;

    constructor(target, size, showbox) {
        super(target);
        var innerInstrument = super.getInstrumentDiv();
        innerInstrument.className = "heading";
        innerInstrument.innerHTML = '\
        <img src="img/heading_back.svg" class="heading-pointer box"/>\
        <img src="img/heading_mechanics.svg" class="box"/>';
        super.resize(size);
        super.showBox(showbox);

        // Get reference to moving element
        this.#headingPointer = innerInstrument.querySelector('img.heading-pointer');

        this.setHeading(0);
    }

    setHeading(heading) {
        this.#headingPointer.style.transform = `rotate(${heading}deg)`;
    }
};

class Altimeter extends Instrument {
    static max = 999999; // Six digit Counter Limit
    static space = 264000; // Start of space (ft)
    static wheelsUp = 10; // Start of Sky
    static midnightzone = -1000 // Start of Midnight Zone
    static min = -36000; // Deepest part of sea (ft)
    #needle;
    #counter;
    #flag;

    constructor(target, size, showbox) {
        super(target);
        var innerInstrument = super.getInstrumentDiv();
        innerInstrument.className = "altimeter";
        innerInstrument.innerHTML = '\
        <img src="img/altimeter_back.svg" class="box"/>\
        <div class="counter" >\
            <span class="digit" id="digit-5">0</span>\
            <span class="digit" id="digit-4">0</span>\
            <span class="digit" id="digit-3">0</span>\
            <span class="digit" id="digit-2">0</span>\
            <span class="digit" id="digit-1">0</span>\
            <span class="digit" id="digit-0">0</span>\
        </div>\
        <div class="flag">\
          <img src="img/altimeter_flag_hatch.svg" class="box"/>\
        </div>\
        <img src="img/needle.svg" class="needle box"/>';
        super.resize(size);
        super.showBox(showbox);

        // Get references to moving elements
        this.#needle = innerInstrument.querySelector('div img.needle');
        this.#counter = innerInstrument.querySelector('div.counter');
        this.#flag = innerInstrument.querySelector('div.flag');

        this.#counter.style.fontSize = `${size / Instrument.baseSize * 20}px`;
        this.#counter.style.top = `-${size / 8}px`;

        this.setAltitude(0);
    }

    #setFlag(altitude) {
        var newFlag = "";
        if (altitude > Altimeter.space) {
            newFlag = "space";
        } else if (altitude > Altimeter.wheelsUp) {
            newFlag = "sky";
        } else if (altitude >= 0) {
            newFlag = "hatch";
        } else if (altitude > -Altimeter.midnightzone) {
            newFlag = "sea";
        } else {
            newFlag = "midnightzone";
        }
        this.#flag.innerHTML = `<img src="img/altimeter_flag_${newFlag}.svg" class=" box"/>`;
    }

    #setCounter(altitude) {
        var values = altitude.toString().split('').reverse();
        for (var n = values.length; n != 6; n++) {
            values[n] = '0'  // pad counter with leading zeros
        }
        values.forEach((value, index) => {
            this.#counter.querySelector(`#digit-${index}`).innerHTML = value;
        });
    }

    setAltitude(altitude) {
        if (altitude > Altimeter.max) {
            altitude = Altimeter.max;
        } else if (altitude < Altimeter.min) {
            altitude = Altimeter.min;
        }
        this.#setFlag(altitude);
        altitude = Math.abs(altitude);
        this.#setCounter(altitude);
        var needlePos = 90 + altitude % 1000 * 360 / 1000;
        this.#needle.style.transform = `rotate(${needlePos}deg)`;
    }
};

class AttitudeIndicator extends Instrument {
    static pitchLimit = 90;
    static tickerHeight = 570;
    #pitch;
    #circle;
    #back;
    #pitchTickerHeight;
    #pitchTickerRatio;
    #pitchTickerOffset;
    #currentRoll = 0;
    #currentPitch = 0;

    constructor(target, size, showbox) {
        super(target);
        var innerInstrument = super.getInstrumentDiv();
        innerInstrument.className = "attitude";
        innerInstrument.innerHTML = '\
        <img src="img/attitude_indicator_back.svg" class="back box"/>\
        <img src="img/attitude_indicator_pitch.svg" class="pitch box"/>\
        <img src="img/attitude_indicator_mask.svg" class="box"/>\
        <img src="img/attitude_indicator_circle.svg" class="circle box"/>\
        <img src="img/attitude_indicator_mechanics.svg" class="box"/>';
        super.resize(size);
        super.showBox(showbox);

        // Get references to moving elements
        this.#pitch = innerInstrument.querySelector('img.pitch');
        this.#back = innerInstrument.querySelector('img.back');
        this.#circle = innerInstrument.querySelector('img.circle');

        // set pitch ticker strip height
        this.#pitchTickerHeight = AttitudeIndicator.tickerHeight * (size / Instrument.baseSize);
        this.#pitchTickerRatio = AttitudeIndicator.tickerHeight / this.#pitchTickerHeight;
        this.#pitch.style.width = size;
        this.#pitch.style.height = `${this.#pitchTickerHeight}px`;
        this.#currentRoll = 0;
        this.#currentPitch = 0;
        this.#pitchTickerOffset = (this.#pitchTickerHeight - size) / 2;
        this.#updatePitch();
    }

    #updatePitch() {
        this.#back.style.transform = `rotate(${this.#currentRoll}deg)`;
        this.#circle.style.transform = `rotate(${this.#currentRoll}deg)`;
        var x = (this.#pitchTickerHeight / 2) - this.#currentPitch;
        this.#pitch.style.transformOrigin = `50% ${x}px`;
        this.#pitch.style.transform = `translateY(${this.#currentPitch - this.#pitchTickerOffset}px) rotate(${this.#currentRoll}deg)`;
    }

    setRoll(roll) {
        this.#currentRoll = roll;
        this.#updatePitch();
    }

    setPitch(pitch) {
        if (pitch > AttitudeIndicator.pitchLimit) {
            pitch = AttitudeIndicator.pitchLimit;
        } else if (pitch < -AttitudeIndicator.pitchLimit) {
            pitch = -AttitudeIndicator.pitchLimit;
        }
        this.#currentPitch = pitch * 3 / this.#pitchTickerRatio;
        this.#updatePitch();
    }
};


class VerticalSpeedIndicator extends Instrument {

    static limit = 1.95;
    #needle

    constructor(target, size, showbox) {
        super(target);
        var innerInstrument = super.getInstrumentDiv();
        innerInstrument.className = "vsi";

        innerInstrument.innerHTML = '\
        <img src="img/vertical_back.svg" class="box"/>\
        <img src="img/needle.svg" class="needle box"/>';
        super.resize(size);
        super.showBox(showbox);

        // Get reference to moving element
        this.needle = innerInstrument.querySelector('div img.needle');

        this.setVsi(0);
    }

    setVsi(verticalSpeed) {
        if (verticalSpeed > VerticalSpeedIndicator.limit) {
            verticalSpeed = VerticalSpeedIndicator.limit;
        } else if (verticalSpeed < -VerticalSpeedIndicator.limit) {
            verticalSpeed = -VerticalSpeedIndicator.limit;
        }
        verticalSpeed = verticalSpeed * 90;
        this.needle.style.transform = `rotate(${verticalSpeed}deg)`;
    }
};


class Radar extends Instrument {
    #beam;
    #screen;
    #radius;
    #blipsize;
    #scanTime;

    constructor(target, scantime, size, showbox) {
        super(target);
        var innerInstrument = super.getInstrumentDiv();
        innerInstrument.className = "radar";
        innerInstrument.innerHTML = '\
        <img src="img/radar_back.svg" class="box"/>\
        <img src="img/radar_beam.svg" class="beam box"/>\
        <div class="screen"></div>';
        super.resize(size);
        super.showBox(showbox);

        // Get reference to moving element
        this.#beam = innerInstrument.querySelector('img.beam');
        this.#screen = innerInstrument.querySelector('div.screen');
        this.#screen.style.width = size;
        this.#screen.style.height = size;

        this.#radius = size / 2;
        this.#blipsize = size / 20;
        this.#scanTime = scantime;
        this.setBeam(90);
    }

    setBeam(angle) {
        this.#beam.style.transform = `rotate(${angle}deg)`;
    }

    // Radar beam moves automatically
    autoBeam() {
        this.#beam.classList.add('autoradarbeam');
        this.#beam.style.animationDuration = `${this.#scanTime}s`;
    }

    // Creates radar blips (targets) that automatically animate to match autobeam rotation
    plotAutoBlips(numberOfBlips) {
        for (var n = 0; n != numberOfBlips; n++) {
            var blip = document.createElement('div');
            blip.className = "target-blip";
            var distanceFromCenter = Math.random() * (this.#radius * 2 / 3);
            var angle = Math.random() * (Math.PI * 2.00);
            var delay = (this.#scanTime / (Math.PI * 2.00)) * angle;
            var x = (Math.cos(angle) * distanceFromCenter) + this.#radius - (this.#blipsize / 2);
            var y = (Math.sin(angle) * distanceFromCenter) + this.#radius - (this.#blipsize / 2);
            blip.style.width = this.#blipsize;
            blip.style.height = this.#blipsize;
            blip.style.borderRadius = `${this.#blipsize / 2}px`;
            blip.style.left = x;
            blip.style.top = y;
            blip.style.animationDelay = `${delay}s`;
            blip.style.animationDuration = `${this.#scanTime}s`;
            this.#screen.append(blip);
        }
    }
};