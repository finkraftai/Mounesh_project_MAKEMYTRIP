import React, { useState } from 'react';
import { Button, Modal, Progress } from 'antd';
import './App.css';
import logoImage from './make-my-trip-1-260x146-removebg-preview.png';


function App() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [expenseClientId, setExpenseClientId] = useState('');
  const [externalOrgId, setExternalOrgId] = useState('');
  const [collectionName, setCollectionName] = useState('');
  const [Row_Labels, setRow_Labels] = useState('');
  const [Org_name, setOrg_name] = useState('');
  const [Admin_Email_1, setAdmin_Email_1] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [progressPercent, setProgressPercent] = useState(0);
  const [openModal, setOpenModal] = useState(false);
  const [modalMessage, setModalMessage] = useState('');
  const [errorModalVisible, setErrorModalVisible] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitted(true);
  
    const startDateObj = new Date(startDate);
    const endDateObj = new Date(endDate);
  
    // Calculate the difference in months between start and end dates
    const monthDiff = (endDateObj.getFullYear() - startDateObj.getFullYear()) * 12 +
      endDateObj.getMonth() - startDateObj.getMonth();
  
    // Check if the difference is exactly 12 months
    if (monthDiff !== 12) {
      setErrorMessage('Start and end dates must be exactly 12 months apart.');
      setErrorModalVisible(true);
      setIsSubmitted(false);
      return;
    }
  
    // Loop 12 times to submit data for each month
    for (let i = 0; i < 12; i++) {
      const startOfMonth = new Date(startDateObj);
      startOfMonth.setMonth(startDateObj.getMonth() + i);
  
      const endOfMonth = new Date(startOfMonth);
      endOfMonth.setMonth(startOfMonth.getMonth() + 1);
      endOfMonth.setDate(endOfMonth.getDate() - 1); // Set to last day of the month
  
      const data = {
        start_date: startOfMonth.toISOString().slice(0, 10), // Format as YYYY-MM-DD
        end_date: endOfMonth.toISOString().slice(0, 10), // Format as YYYY-MM-DD
        'expense-client-id': expenseClientId,
        'external-org-id': externalOrgId,
        collection_name: collectionName,
        'Admin_Email_1':Admin_Email_1,
        'Org_name':Org_name,
        'Row_Labels':Row_Labels

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
  
        // Handle successful response
        if (response.ok) {
          // Log the response data for debugging
          console.log('Response Data:', responseData);
          // Handle success as needed
        } else {
          // Handle other response statuses (e.g., error responses)
          throw new Error(responseData.message || 'Failed to submit data');
        }
      } catch (error) {
        console.error('Error:', error);
        // Handle error here, such as showing an error message to the user
      }
    }
  
    // Reset the submission state
    setIsSubmitted(false);
  };
  

  const handleModalOk = () => {
    setOpenModal(false);
    setIsSubmitted(false);
    setProgressPercent(0);
    setStartDate('');
    setEndDate('');
    setExpenseClientId('');
    setExternalOrgId('');
    setCollectionName('');
    setOrg_name('');
    setRow_Labels('');
    setAdmin_Email_1('');
  };

  const handleModalCancel = () => {
    setOpenModal(false);
    setIsSubmitted(false);
  };

  return (
    <div className="App">
      <img src={logoImage} alt="Logo" style={{ position: 'absolute', left: '10px', top: '10px' }} /> {/* Add your image here */}
      <form className="custom-form" onSubmit={handleSubmit}>
        <div className="input-group">
          <label style={{ marginLeft: "-54px" }}>Start Date :</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            disabled={isSubmitted}
            required
            style={{ width: "100px" }}
          />
        </div>
        <div className="input-group">
          <label style={{ marginLeft: "-54px" }}>End Date :</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            disabled={isSubmitted}
            required
            style={{ width: "100px" }}
          />
        </div>
        <div className="input-group">
          <label>expenseClientId</label>
          <input
            type="text"
            value={expenseClientId}
            onChange={(e) => setExpenseClientId(e.target.value)}
            disabled={isSubmitted}
            required
          />
        </div>
        <div className="input-group">
          <label>externalOrgId :</label>
          <input
            type="text"
            value={externalOrgId}
            onChange={(e) => setExternalOrgId(e.target.value)}
            disabled={isSubmitted}
            required
          />
        </div>
        <div className="input-group">
          <label>Folder Name:</label>
          <input
            type="text"
            value={collectionName}
            onChange={(e) => setCollectionName(e.target.value)}
            disabled={isSubmitted}
            required
          />
        </div>
        <div className="input-group">
          <label>Row_Labels:</label>
          <input
            type="text"
            value={Row_Labels}
            onChange={(e) => setRow_Labels(e.target.value)}
            disabled={isSubmitted}
            required
          />
        </div>
        <div className="input-group">
          <label>Org_name:</label>
          <input
            type="text"
            value={Org_name}
            onChange={(e) => setOrg_name(e.target.value)}
            disabled={isSubmitted}
            required
          />
        </div>
        <div className="input-group">
          <label>Admin_Email_1:</label>
          <input
            type="text"
            value={Admin_Email_1}
            onChange={(e) => setAdmin_Email_1(e.target.value)}
            disabled={isSubmitted}
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
