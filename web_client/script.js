const prescriptionTableBody = document.getElementById('prescriptionBody');
let accessToken = '';  // Variable to store the access token

// Function to obtain the access token
function obtainAccessToken() {
    const clientId = 'client_id_1';  // Ensure this matches your OAuth server
    const clientSecret = 'client_secret_1';  // Ensure this matches your OAuth server

    fetch('http://127.0.0.1:3001/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `grant_type=client_credentials&client_id=${clientId}&client_secret=${clientSecret}`
    })
    .then(response => {
        console.log('Response:', response);
        if (!response.ok) {
            throw new Error('Failed to obtain access token');
        }
        return response.json();
    })
    .then(data => {
        if (data.access_token) {
            accessToken = data.access_token;  // Store the access token
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
document.getElementById('prescriptionForm').addEventListener('submit', postPrescriptionData);

// Fetch all prescriptions
function fetchAllPrescriptions() {
    console.log('Fetching all prescriptions');
    console.log(accessToken);
    fetch('http://127.0.0.1:3000/t-prescription-all', {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${accessToken}`  // Use the stored access token
        }
    })
    .then(response =>{
        console.log(response)
        return response.json()
    })
    .then(data => {
        console.log(data)
        populateTable(data);
    })
    .catch(error => {
        console.error('Error fetching all prescriptions:', error);
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

// Post prescription data
function postPrescriptionData(event) {
    event.preventDefault();  // Prevent form submission

    const prescriptionId = document.getElementById('prescriptionId').value;
    const patientName = document.getElementById('patientName').value;
    const medication = document.getElementById('medication').value;
    const dispenseDate = document.getElementById('dispenseDatePost').value;
    const offLabelUse = document.getElementById('offLabelUse').value;

    const csvData = `${prescriptionId},${patientName},${medication},${dispenseDate},${offLabelUse}`;

    fetch('http://127.0.0.1:3000/t-prescription-carbon-copy', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,  // Use the stored access token
            'Content-Type': 'text/csv'
        },
        body: csvData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Post Response:', data);
        alert('Prescription data posted successfully!');
    })
    .catch(error => {
        console.error('Error posting prescription data:', error);
    });
}

// Populate the table with fetched data
function populateTable(data) {
    prescriptionTableBody.innerHTML = '';  // Clear existing rows
    data.forEach(prescription => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${prescription.prescription_id}</td>
            <td>${prescription.patient_name}</td>
            <td>${prescription.medication}</td>
            <td>${prescription.dispense_date}</td>
            <td>${prescription.off_label_use ? 'Yes' : 'No'}</td>
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
