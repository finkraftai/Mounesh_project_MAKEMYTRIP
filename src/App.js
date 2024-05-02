import React, { useState } from 'react';
import { Button, Modal, Progress, Upload } from 'antd';
import * as XLSX from 'xlsx';
import './App.css';
import logoImage from './make-my-trip-1-260x146-removebg-preview.png';
import fetch from 'cross-fetch';

function App() {
  // State variables
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [collectionName, setCollectionName] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [progressPercent, setProgressPercent] = useState(0);
  const [fileData, setFileData] = useState(null);
  const [openModal, setOpenModal] = useState(false);
  const [modalMessage, setModalMessage] = useState('');
  const [errorModalVisible, setErrorModalVisible] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Function to handle file upload
  const handleFileUpload = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const workbook = XLSX.read(e.target.result, { type: 'binary' });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(sheet);
      const transformedData = data.map(row => ({
        Row_Labels: parseInt(row.Row_Labels),
        Org_name: row.Org_name && row.Org_name.trim(),
        Admin_Email_1: row.Admin_Email_1 && row.Admin_Email_1.trim(),
        expenseClientId: row.Expense_Client_Id && row.Expense_Client_Id.trim(),
        externalOrgId: row.External_Org_Id && row.External_Org_Id.trim(),
      }));
      setFileData(transformedData);
    };
    reader.readAsBinaryString(file);
  };

  // Function to handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitted(true);
    const startDateObj = new Date(startDate);
    const endDateObj = new Date(endDate);
    const monthDiff = (endDateObj.getFullYear() - startDateObj.getFullYear()) * 12 +
    endDateObj.getMonth() - startDateObj.getMonth();

    if (monthDiff !== 12) {
      setErrorMessage('Start and end dates must be exactly 12 months apart.');
      setErrorModalVisible(true);
      setIsSubmitted(false);
      return;
    }
    for (let i = 0; i < fileData.length; i++) {
      const rowData = fileData[i];
    // Loop for each month and submit data
    for (let i = 0; i < 12; i++) {
      const startOfMonth = new Date(startDateObj);
      startOfMonth.setMonth(startDateObj.getMonth() + i);

      const endOfMonth = new Date(startOfMonth);
      endOfMonth.setMonth(startOfMonth.getMonth() + 1);
      endOfMonth.setDate(endOfMonth.getDate() - 1);

      // const rowData = fileData[i % fileData.length]; // Accessing fileData based on loop index
      
      // console.log('Data to senddddddddddddd:', rowData);
      const data = {
        start_date: startOfMonth.toISOString().slice(0, 10),
        end_date: endOfMonth.toISOString().slice(0, 10),
        'expense-client-id': rowData.expenseClientId,
        'external-org-id': rowData.externalOrgId,
        collection_name: collectionName,
        'Admin_Email_1': rowData.Admin_Email_1,
        'Org_name': rowData.Org_name,
        'Row_Labels': rowData.Row_Labels
      };

      console.log('Data to send:', data); // Log data before sending

      try {
        const response = await fetch('http://127.0.0.1:5000/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        console.log('Response:', response); // Log the response

        const responseData = await response.json();

        if (response.ok) {
          console.log('Response Data:', responseData);
          // Handle success as needed
        } else {
          throw new Error(responseData.message || 'Failed to submit data');
        }
      } catch (error) {
        console.error('Error:', error);
        // Handle error here, such as showing an error message to the user
      }
    }
  }
    setIsSubmitted(false);
  };

  // Function to handle modal cancel
  const handleModalCancel = () => {
    setOpenModal(false);
    // Additional logic if needed
    setIsSubmitted(false);
  };

  // Function to handle modal OK
  const handleModalOk = () => {
    setOpenModal(false);
    setIsSubmitted(false);
    setProgressPercent(0);
    setStartDate('');
    setEndDate('');
    setCollectionName('');
    setFileData(null);
  };

  // JSX code for UI

  return (
    <div className="App">
      <img src={logoImage} alt="Logo" style={{ position: 'absolute', left: '10px', top: '10px' }} />
      <form className="custom-form" onSubmit={handleSubmit}>
        <Upload
          accept=".xlsx,.xls"
          beforeUpload={file => {
            handleFileUpload(file);
            return false;
          }}
          showUploadList={false}
        >
          <Button>Upload XLSX File</Button>
        </Upload>
        {fileData && (
          <div>
            <p>File Uploaded Successfully!</p>
            <ul>
            </ul>
          </div>
        )}
        <div className="input-group">
          <label>Start Date :</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
          />
        </div>
        <div className="input-group">
          <label>End Date :</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
          />
        </div>
        <div className="input-group">
          <label>Folder Name:</label>
          <input
            type="text"
            value={collectionName}
            onChange={(e) => setCollectionName(e.target.value)}
            required
          />
        </div>
        <Button type="primary" htmlType="submit" disabled={isSubmitted}>
          Submit
        </Button>
      </form>
      <Modal
        title={isSubmitted ? "Work in Progress" : "Data Saved Successfully"}
        visible={isSubmitted || openModal}
        closable={!isSubmitted}
        footer={null}
        onCancel={handleModalCancel}
      >
        {isSubmitted ? <Progress percent={progressPercent} /> : <p>{modalMessage}</p>}
        {!isSubmitted && (
          <Button type="primary" onClick={handleModalOk}>
            OK
          </Button>
        )}
      </Modal>
      <Modal
        title="Error"
        visible={errorModalVisible}
        closable={false}
        footer={[
          <Button key="ok" onClick={() => setErrorModalVisible(false)}>
            OK
          </Button>
        ]}
      >
        <p>{errorMessage}</p>
      </Modal>
    </div>
  );
}

export default App;
