"use strict";

class Instrument{
    static baseSize = 375;
    #pointer;
    #applyLimits = false;
    #min = 0;
    #max = 0;
 
     constructor(target, size = this.baseSize, markup, applyLimits = false, min = 0, max = 0, initialOffset = 0) {
        var instrument = document.getElementById(target);
        instrument.innerHTML = markup;
        instrument.style.width = instrument.style.height = size;
        this.#pointer = instrument.querySelector('img.pointer'); // Find the moving element in the passed in html
        this.#min = min;
        this.#max = max;
        this.#applyLimits = applyLimits;
        this.instrument = instrument;
        this.position = initialOffset;
     };
 
     set position(_pos) {
        if(this.#applyLimits) {
            if (_pos > this.#max) {
                _pos = this.#max;
            } else if (_pos < this.#min) {
                _pos = this.#min;
            }
        }
        this.#pointer.style.transform = `rotate(${_pos}deg)`;
     };
 };


 class AirSpeed extends Instrument{

    constructor(target, size) {
        var markup = `
            <div class="instrument">
                <img src="img/airspeed_dial.svg" class="dial"/>
                <img src="img/needle.svg" class="pointer dial"/>
                <img src="img/instrument_ring.svg" class="dial"/>
            </div>`;
        super(target, size, markup, true, 0, 320); // airspeed range 0 to 800
    }

    set speed(speed) {
        super.position = (speed * 360) / 900;
    }
};


class VerticalSpeedIndicator extends Instrument{

    constructor(target, size) {
        var markup = `
            <div class="instrument">
                <img src="img/vertical_dial.svg" class="dial"/>
                <img src="img/needle.svg" class="pointer dial"/>
                <img src="img/instrument_ring.svg" class="dial"/>
            </div>`;
        super(target, size, markup, true , -261, 81, -90); // vertical speed range -1900 to 1900
    }

    set rateOfClimb(verticalSpeed) {
        super.position = (verticalSpeed * 90) / 1000 - 90;
    }
};


class Heading extends Instrument{

    constructor(target, size) {
        var markup = `
            <div class="instrument">
                <img src="img/heading_dial.svg" class="pointer dial"/>
                <img src="img/heading_glass.svg" class="dial"/>
                <img src="img/instrument_ring.svg" class="dial"/>
            </div>`;
        super(target, size, markup);
    }

    set direction(heading) {
        super.position = heading % 360;
    }
};


class Altimeter extends Instrument{
    static max = 999999; // Six digit Counter Limit
    static space = 264000; // Start of space (ft)
    static wheelsUp = 10; // Airborne
    static midnightzone = -1000 // Start of Midnight Zone
    static min = -36000; // Deepest part of sea (ft)
    #id;

    constructor(target, size) {
        var id = `altimeter-${crypto.randomUUID()}`;
        var markup = `
            <div class="instrument">
                <img src="img/altimeter_dial.svg" class="dial"/>
                <img src="img/altimeter_flag_hatch.svg" id="${id}-flag" class="dial"/>
                <div class="counter" >
                    <span class="digit" id="${id}-d5">0</span>
                    <span class="digit" id="${id}-d4">0</span>
                    <span class="digit" id="${id}-d3">0</span>
                    <span class="digit" id="${id}-d2">0</span>
                    <span class="digit" id="${id}-d1">0</span>
                    <span class="digit" id="${id}-d0">0</span>
                </div>
                <img src="img/needle.svg" class="pointer dial"/>
                <img src="img/instrument_ring.svg" class="dial"/>
            </div>`;
        super(target, size, markup);
        var counter = this.instrument.querySelector('div.counter');
        counter.style.fontSize = `${size / Instrument.baseSize * 20}px`;
        counter.style.top = `-${size / 8}px`;
        this.#id = id;
    }

    #setFlag(altitude) {
        var newFlag = "";
        if (altitude > Altimeter.space) {
            newFlag = "space";
        } else if (altitude > Altimeter.wheelsUp) {
            newFlag = "sky";
        } else if (altitude >= 0) {
            newFlag = "hatch";
        } else if (altitude > Altimeter.midnightzone) {
            newFlag = "sea";
        } else {
            newFlag = "midnightzone";
        }
        document.getElementById(`${this.#id}-flag`).src = `img/altimeter_flag_${newFlag}.svg`
    }

    #setCounter(altitude) {
        var values = altitude.toString().split('').reverse();
        for (var n = values.length; n != 6; n++) {
            values[n] = '0'  // pad counter with leading zeros
        }
        values.forEach((value, index) => {
            document.getElementById(`${this.#id}-d${index}`).innerText = value;
        });
    }

    set altitude(altitude) {
        if (altitude > Altimeter.max) {
            altitude = Altimeter.max;
        } else if (altitude < Altimeter.min) {
            altitude = Altimeter.min;
        }
        this.#setFlag(altitude);
        altitude = Math.abs(altitude);
        this.#setCounter(altitude);
        super.position = altitude % 1000 * 360 / 1000;
    }
};


class AttitudeIndicator extends Instrument{
    static pitchLimit = 90;
    static tickerHeight = 570;
    #pitch;
    #roll;
    #pitchTickerHeight;
    #pitchTickerRatio;
    #pitchTickerOffset;
    #currentRoll = 0;
    #currentPitch = 0;

    constructor(target, size) {
        var markup = `
            <div class="instrument">
                <img src="img/attitude_indicator_horizon.svg" class="pointer dial"/>
                <img src="img/attitude_indicator_pitch.svg" class="pitch dial"/>
                <img src="img/attitude_indicator_pitch_mask.svg" class="dial"/>
                <img src="img/attitude_indicator_roll.svg" class="roll dial"/>
                <img src="img/attitude_indicator_glass.svg" class="dial"/>
                <img src="img/instrument_ring.svg" class="dial"/>
            </div>`;
        super(target, size, markup);

        // Get references to moving elements
        this.#pitch = this.instrument.querySelector('img.pitch');
        this.#roll = this.instrument.querySelector('img.roll');

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
        super.position = this.#currentRoll; // Rotate Horizon
        this.#roll.style.transform = `rotate(${this.#currentRoll}deg)`;
        this.#pitch.style.transformOrigin = `50% ${(this.#pitchTickerHeight / 2) - this.#currentPitch}px`;
        this.#pitch.style.transform = `translateY(${this.#currentPitch - this.#pitchTickerOffset}px) rotate(${this.#currentRoll}deg)`;
    }

    set roll(roll) {
        this.#currentRoll = roll;
        this.#updatePitch();
    }

    set pitch(pitch) {
        if (pitch > AttitudeIndicator.pitchLimit) {
            pitch = AttitudeIndicator.pitchLimit;
        } else if (pitch < -AttitudeIndicator.pitchLimit) {
            pitch = -AttitudeIndicator.pitchLimit;
        }
        this.#currentPitch = pitch * 3 / this.#pitchTickerRatio;
        this.#updatePitch();
    }
};


class Radar {
    #beam;
    #screen;
    #radius;
    #blipsize;
    #scanTime;

    constructor(target, scantime, size) {
        var instrument =  document.getElementById(target);
        instrument.innerHTML = `
            <div class="instrument">
                <img src="img/radar_screen.svg" class="dial"/>
                <img src="img/radar_beam.svg" class="beam dial"/>
                <div class="screen"></div>
                <img src="img/instrument_ring.svg" class="dial"/>
            </div>`;
        instrument.style.width = instrument.style.height = size;

        // Get reference to moving element
        this.#beam = instrument.querySelector('img.beam');
        this.#screen = instrument.querySelector('div.screen');
        this.#screen.style.width = size;
        this.#screen.style.height = size;

        this.#radius = size / 2;
        this.#blipsize = size / 20;
        this.#scanTime = scantime;
        this.setBeam(0);
    }

    setBeam(angle) {
        this.#beam.style.transform = `rotate(${angle}deg)`;
    }

    // Radar beam moves automatically
    autoBeam() {
        this.#beam.classList.add('autoradarbeam');
        this.#beam.style.animationDuration = `${this.#scanTime}s`;
    }

    // Creates ramdomly placed radar blips (targets) that automatically animate to match autobeam rotation
    // I.e. as the radar beam appears to pass over them they will illuminate and then slowly decay back to a dark state
    plotAutoBlips(numberOfBlips) {
        var max = (this.#radius * 4 / 5) - (this.#blipsize / 2)
        var min = (this.#radius / 6)
        var halfBlip = this.#blipsize / 2
        for (var n = 0; n != numberOfBlips; n++) {
            var distanceFromCenter = Math.random() * (max - min) + min;
            var angle = Math.random() * (Math.PI * 2.00);
            var x = (Math.cos(angle) * distanceFromCenter) + this.#radius - halfBlip;
            var y = (Math.sin(angle) * distanceFromCenter) + this.#radius - halfBlip;
            var touchAngle = angle - (Math.atan(halfBlip / distanceFromCenter));
            var delay = (this.#scanTime / (Math.PI * 2.00)) * touchAngle;
            
            var blip = document.createElement('div');
            blip.className = "target-blip";
            blip.style.width = this.#blipsize;
            blip.style.height = this.#blipsize;
            blip.style.borderRadius = `${halfBlip}px`;
            blip.style.left = x;
            blip.style.top = y;
            blip.style.animationDelay = `${delay}s`;
            blip.style.animationDuration = `${this.#scanTime}s`;
            this.#screen.append(blip);
        }
    }
};