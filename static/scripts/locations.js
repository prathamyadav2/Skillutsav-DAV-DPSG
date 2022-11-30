
function get_states(state_id) {
	var state_dropdown = document.getElementById(state_id);
	fetch('../static/datasets/states.json')
        .then(response => response.json())
        .then(data => {
            for (var i = 1; i < data.states.length; i++) {
                state_dropdown.options[state_dropdown.length] = new Option(data.states[i], data.states[i]);
            }
        }
    )
}

function get_cities(city_id, state_name) {
	var city_dropdown = document.getElementById(city_id);
    fetch('../static/datasets/cities.json')
        .then(response => response.json())
        .then(data => {
            for (var i = 1; i < data[state_name].length; i++) {
                city_dropdown.options[city_dropdown.length] = new Option(data[state_name][i], data[state_name][i]);
            }
        }
    )
}

