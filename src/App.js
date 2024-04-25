import React, { useState } from 'react';
import { Button, Modal, Progress } from 'antd';
import './App.css';
import logoImage from './make-my-trip-1-260x146-removebg-preview.png'; // Import your image here

function App() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [expenseClientId, setExpenseClientId] = useState('');
  const [externalOrgId, setExternalOrgId] = useState('');
  const [collectionName, setCollectionName] = useState('');
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
    const diffInDays = Math.abs((endDateObj - startDateObj) / (1000 * 60 * 60 * 24));

    if (diffInDays > 30) {
      setErrorMessage('Please enter a date range within 1 month.');
      setErrorModalVisible(true);
      setIsSubmitted(false);
      return;
    }

    const data = {
      start_date: startDate,
      end_date: endDate,
      'expense-client-id': expenseClientId,
      'external-org-id': externalOrgId,
      collection_name: collectionName
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

        // Update modal message and open the modal
        setModalMessage(responseData.message);
        setOpenModal(true);

        // Reset the submission state and progress
        setIsSubmitted(false);
        setProgressPercent(0);
      } else {
        // Handle other response statuses (e.g., error responses)
        throw new Error(responseData.message || 'Failed to submit data');
      }
    } catch (error) {
      console.error('Error:', error);
      setIsSubmitted(false);
      // Handle error here, such as showing an error message to the user
    }
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
