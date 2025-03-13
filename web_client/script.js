const prescriptionTableBody = document.getElementById('prescriptionBody');
let accessToken = '';  // Variable to store the access token

// Function to obtain the access token
function obtainAccessToken() {
    console.log("Attempting to obtain access token...");
    const clientId = 'client_bfarm_webclient';
    const clientSecret = 'client_secret_bfarm_webclient';

    fetch('http://127.0.0.1:3001/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `grant_type=client_credentials&client_id=${clientId}&client_secret=${clientSecret}`
    })
    .then(response => {
        console.log('Token Response:', response);
        if (!response.ok) {
            throw new Error('Failed to obtain access token');
        }
        return response.json();
    })
    .then(data => {
        if (data.access_token) {
            accessToken = data.access_token;
            console.log('Access Token:', accessToken);
        } else {
            throw new Error('Access token not found in response');
        }
    })
    .catch(error => {
        console.error('Error obtaining access token:', error);
        alert('Failed to obtain access token. Please check the console for more details.');
    });
}

document.getElementById('fetchByDate').addEventListener('click', fetchPrescriptionsByDate);
document.getElementById('fetchOffLabel').addEventListener('click', fetchOffLabelPrescriptions);
document.getElementById('fetchAll').addEventListener('click', fetchAllPrescriptions);
document.getElementById('createDispense').addEventListener('click', createDispense);
document.getElementById('deleteAll').addEventListener('click', deleteAllPrescriptions);

// Fetch all prescriptions
function fetchAllPrescriptions() {
    console.log('Fetching all prescriptions');
    fetch('http://127.0.0.1:3000/t-prescription-all', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`  // Use the stored access token
        }
    })
    .then(response => {
        console.log('Response:', response);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data) {
            if (data.message) {
                message = data.message;
                alert(message);
            } else {
                populateTable(data);
            }
        }
    })
    .catch(error => {
        console.error('Error fetching all prescriptions:', error);
        alert('An error occurred while fetching prescriptions. Please check the console for more details.');
    });
}


// Fetch prescriptions by dispense date
function fetchPrescriptionsByDate() {
    const dispenseDate = document.getElementById('dispenseDate').value;
    if (!dispenseDate) {
        alert('Please select a dispense date.');
        return;
    }

    fetch(`http://127.0.0.1:3000/t-prescription-by-date?dispense_date=${dispenseDate}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`  // Use the stored access token
        }
    })
    .then(response => response.json())
    .then(data => {
        populateTable(data);
    })
    .catch(error => {
        console.error('Error fetching prescriptions:', error);
    });
}

// Fetch all prescriptions with off-label use
function fetchOffLabelPrescriptions() {
    fetch('http://127.0.0.1:3000/t-prescription-off-label-use', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`  // Use the stored access token
        }
    })
    .then(response => response.json())
    .then(data => {
        populateTable(data);
    })
    .catch(error => {
        console.error('Error fetching off-label prescriptions:', error);
    });
}

// Create a new dispense
function createDispense() {
    console.log('Creating a new dispense');
    fetch('http://127.0.0.1:3002/dispense', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,  // Use the stored access token
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            // Add any necessary data for the dispense creation here
            // Example: prescription_id, patient_name, etc.
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to create dispense');
        }
        return response.json();
    })
    .then(data => {
        console.log('Dispense created:', data);
        alert('Dispense created successfully!');
    })
    .catch(error => {
        console.error('Error creating dispense:', error);
        alert('Failed to create dispense. Please check the console for more details.');
    });
}

// Delete all prescriptions
function deleteAllPrescriptions() {
    console.log('Deleting all prescriptions');
    fetch('http://127.0.0.1:3000/delete-prescriptions', {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${accessToken}`  // Use the stored access token
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete prescriptions');
        }
        alert('All prescriptions deleted successfully!');
        prescriptionTableBody.innerHTML = '';  // Clear the table
    })
    .catch(error => {
        console.error('Error deleting prescriptions:', error);
        alert('Failed to delete prescriptions. Please check the console for more details.');
    });
}

// Populate the table with fetched data
function populateTable(data) {
    prescriptionTableBody.innerHTML = '';  // Clear existing rows
    data.forEach(prescription => {
        // Convert date from yyyy-mm-dd to dd.mm.yyyy
        const [year, month, day] = prescription.dispense_date.split('-');
        const formattedDate = `${day}.${month}.${year}`;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${prescription.prescription_id}</td>
            <td>${prescription.patient_name}</td>
            <td>${prescription.medication}</td>
            <td>${formattedDate}</td>
            <td>${prescription.off_label_use ? 'Yes' : 'No'}</td>
            <td>${prescription.pharmacy}</td>
            <td>${prescription.doctor}</td>
        `;
        prescriptionTableBody.appendChild(row);
    });
}


// Function to sort the table by column index
function sortTable(columnIndex) {
    const table = document.getElementById('prescriptionTable');
    const rows = Array.from(table.rows).slice(1);  // Exclude header row
    const isAscending = table.getAttribute('data-sort-order') === 'asc';

    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].innerText;
        const bText = b.cells[columnIndex].innerText;

        return isAscending
            ? aText.localeCompare(bText)
            : bText.localeCompare(aText);
    });

    // Clear the table body and append sorted rows
    prescriptionTableBody.innerHTML = '';
    rows.forEach(row => prescriptionTableBody.appendChild(row));

    // Toggle sort order
    table.setAttribute('data-sort-order', isAscending ? 'desc' : 'asc');
}

// Obtain the access token when the page loads
window.onload = obtainAccessToken;
