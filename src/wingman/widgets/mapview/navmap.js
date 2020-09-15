/*
Copyright © 2016-2017, 2020 biqqles.

This file is part of Wingman.

Wingman is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Wingman is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Wingman.  If not, see <http://www.gnu.org/licenses/>.

This file contains code to modify the default behaviour and appearance
of Space's online navmap (<http://space.discoverygc.com/navmap/>) to
make it suitable for integration into Wingman, as well as providing
functions that can be called from Wingman to perform various actions.
*/

class Wingman {
    constructor() {
        this.head = $('head');
        this.body = $('body');
        this.searchField = $('#searchField');

        // config switches
        this.autoScale = $('#switch6')[0];
        this.showLabels = $('#switch11')[0];
        this.showWrecks = $('#switch1')[0];
        this.showZones = $('#switch2')[0];

        this.initialiseNavmap();
    }

    initialiseNavmap() {
        // Modifies the navmap's document so that it works better for our purposes
        this.setBackgroundColour('transparent');  // remove background image and set a transparent background
        this.setState(this.autoScale, true); // activate 'auto-scale' - required to fill the widget properly

        this.body.css({'overflow': 'hidden',  // hide scrollbars
                       'margin': '0',
                       'padding': '0em'});  // remove margin and padding - required to fill the widget properly

        $('.mapContainer').css({'border': 'none',  // hide border,
                               'box-shadow': 'none', // border shadow,
                               'width': '100vw',  // and fill the widget completely
                               'height': '100vw',
                               'top': '0'});

        $('.navContainer').css('display', 'none'); // hide the navigation panel (removing it prevents the navmap from loading fully)

        $('.mapLegend').css({'border': 'none',  // hide border
                            'top': '-0.2em'}); // prevent universe map legend from obscuring the top of the map

        // miscellaneous behaviour modifications
        document.onmousedown = () => false;  // disable the ability to highlight text...
        $('<style type="text/css">body{cursor: pointer;}</style>').appendTo(this.head);  // and the 'I' selection cursor

        // hook generateMap and generateUniverseMap. Not very pleasant, but I don't believe there's a better way
        const originalGenMap = generateMap;
        generateMap = (system) => {
            originalGenMap(system);
            this.onDisplayChanged();
        }
        const originalGenUniverse = generateUniverseMap;
        generateUniverseMap = () => {
            originalGenUniverse();
            this.onDisplayChanged();
        }
    }

    displayMap(name) {
        // Displays the given item (system or solar)
        this.searchField[0].value = name;
        this.searchField.keyup();
        $('.autocomplete-suggestions').remove();
    }

    displayUniverseMap() {
        // Displays the universe map
        generateUniverseMap();
    }

    onDisplayChanged() {
        // Handle the displayed system or solar being changed
        $('.systemTitle').css('font-size', '2em');

        // Cause clicking on a solar or the grid to update currentSystemNickname and the URL with the solar's nickname or the
        // system's nickname, respectively. Abusing this variable is (very) hacky but convenient because it is reliably updated
        // as soon as a new system is entered.
        const nicknameToUrl = () => updateFragment('q', currentSystemNickname);
        $(".object, .zone").click(function() {
            currentSystemNickname = $(this).attr("data-internal-nickname");
            nicknameToUrl();
        });

        $(".grid").click(function() {
            currentSystemNickname = currentSystem;
            nicknameToUrl();
        });
    }

    getState(configSwitch) {
        // Returns the state of the given switch
        return configSwitch.checked;
    }

    setState(configSwitch, state) {
        // Sets the state of the given switch
        configSwitch.checked = state;
        updateConfigClasses(); // activates config choices
    }

    setBackgroundColour(colour) {
        // Removes the background graphic and sets the given background colour
        $(`<style type='text/css'>body:after{background: ${colour};}</style>`).appendTo(this.head);
    }
}

let wingman = new Wingman();
