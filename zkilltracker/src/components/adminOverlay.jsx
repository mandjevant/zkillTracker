import React, { useState, useEffect } from 'react';
import { TextInput, NumberInput, Modal, Button, Switch, Tabs, FileInput } from '@mantine/core';
import { showNotification } from '@mantine/notifications';
import { posiNotifProps, negaNotifProps } from './helpers';
import axios from 'axios';


export default function AddDataOverlay() {
  const [acCorporationId, setAcCorporationId] = useState('');
  const [amCorporationId, setAmCorporationId] = useState('');
  const [cmcCharacterId, setCmcCharacterId] = useState('');
  const [amCharacterId, setAmCharacterId] = useState('');
  const [amCharacterName, setAmCharacterName] = useState('');
  const [cmcNewCorporationId, setCmcNewCorporationId] = useState('');
  const [approvedCharToAdd, setApprovedCharToAdd] = useState('');
  const [adminCharToAdd, setAdminCharToAdd] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [modalOpened, setModalOpened] = useState(false);
  const [addRemApproved, setAddRemApproved] = useState(true);
  const [addRemAdmin, setAddRemAdmin] = useState(true);
  const [buttonsDisabled, setButtonsDisabled] = useState(false);
  const [ccaCorporationId, setCcaCorporationId] = useState('');
  const [ccaNewAllianceId, setCcaNewAllianceId] = useState('');
  const [file, setFile] = useState(null);

  useEffect(() => {
    let timer;
  
    if (taskId) {
      setButtonsDisabled(true);
  
      timer = setTimeout(() => {
        setTaskId(null);
        setButtonsDisabled(false);
      }, 300000);
    }
  
    return () => {
      clearTimeout(timer);
      setButtonsDisabled(false);
    };
  }, [taskId]);

  async function handleAddCorporation() {
    try {
      await axios.post(`/corporation/add/${acCorporationId}`);
      showNotification({
        message: "Corporation added successfully!",
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: "Failed to add corporation!",
        ...negaNotifProps
      });
    }
  };

  async function handleChangeMemberCorporation() {
    try {
      await axios.post(`/member/${cmcCharacterId}/change_corporation/${cmcNewCorporationId}`);
      showNotification({
        message: "Member corporation changed successfully!",
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: "Failed to change member corporation!",
        ...negaNotifProps
      });
    }
  };

  async function handleChangeCorporationAlliance() {
    try {
      await axios.put(`/corporation/${ccaCorporationId}/change_alliance/${ccaNewAllianceId}`);
      showNotification({
        message: "Corporation alliance changed successfully!",
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: "Failed to change corporation alliance!",
        ...negaNotifProps
      });
    }
  };

  async function handleAddMember() {
    try {
      await axios.post(`/members/add/${amCharacterId}/${amCharacterName}/${amCorporationId}`);
      showNotification({
        message: "Member added successfully!",
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: "Failed to add member!",
        ...negaNotifProps
      });
    }
  };

  async function handleAddKills() {
    try {
      const response = await axios.get(`/kills/add`);
      setTaskId(response.data.task_id);
      showNotification({
        message: "Refresh task started!",
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: "Failed to start refresh task!",
        ...negaNotifProps
      });
    }
  };

  async function handleRefreshCorporations() {
    try {
      const response = await axios.get(`/corporations/refresh`);
      setTaskId(response.data.task_id);
      showNotification({
        message: "Refresh task started!",
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: "Failed to start refresh task!",
        ...negaNotifProps
      });
    }
  }

  async function handleAddMembers() {
    try {
      const response = await axios.get(`/members/add`);
      setTaskId(response.data.task_id);
      showNotification({
        message: "Refresh task started!",
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: "Failed to start refresh task!",
        ...negaNotifProps
      });
    }
  };

  async function handleAddApprovedChar() {
    try {
      if (addRemApproved) {
        await axios.post(`/approved/add/${approvedCharToAdd}`);
      } else {
        await axios.post(`/approved/remove/${approvedCharToAdd}`);
      }
      showNotification({
        message: `Approved character ${ addRemApproved ? "added" : "removed" } successfully!`,
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: `Failed to ${ addRemApproved ? "add" : "remove" } approved character!`,
        ...negaNotifProps
      });
    }
  }

  async function handleAddAdminChar() {
    try {
      if (addRemAdmin) {
        await axios.post(`/admin/add/${adminCharToAdd}`);
      } else {
        await axios.post(`/admin/remove/${adminCharToAdd}`);
      }
      showNotification({
        message: `Admin character ${ addRemAdmin ? "added" : "removed" } successfully!`,
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: `Failed to ${ addRemApproved ? "add" : "remove" } admin character!`,
        ...negaNotifProps
      });
    }
  }

  async function handleConfirmRefresh() {
    setModalOpened(false);
    handleAddMembers();
  };

  const handleAddMonthsData = () => {
    if (!file) {
      showNotification({
        message: "Please select a CSV file before uploading",
        ...negaNotifProps
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    axios.post('/upload_file', formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then(response => {
      showNotification({
        message: ".XLSX file uploaded successfully!",
        ...posiNotifProps
      });
    })
    .catch(error => {
      showNotification({
        message: "Error uploading CSV file",
        ...negaNotifProps
      });
      console.error('Upload error:', error);
    });
  };


  return (
    <div className="adminOverlay">
      <Tabs variant="pills" defaultValue="data">
        <Tabs.List>
          <Tabs.Tab value="data">
            Data
          </Tabs.Tab>
          <Tabs.Tab value="characters">
            Characters
          </Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="data" className="panel">
          <h3 className="adminH3">Add Corporation</h3>
          <div className="rowGroup">
            <NumberInput
              label="Corporation ID"
              value={acCorporationId}
              onChange={(value) => setAcCorporationId(value)}
              min={1}
            />
            <Button
              className="postButton"
              onClick={handleAddCorporation}
              disabled={!acCorporationId}
            >
              Add Corporation
            </Button>
          </div>

          <h3 className="adminH3">Change Corporation Alliance</h3>
          <div className="rowGroup">
            <div className="rowGroupInputs">
              <NumberInput
                label="Corporation ID"
                value={ccaCorporationId}
                onChange={(value) => setCcaCorporationId(value)}
                min={1}
              />
              <NumberInput
                label="New Alliance ID"
                value={ccaNewAllianceId}
                onChange={(value) => setCcaNewAllianceId(value)}
                min={1}
              />
            </div>
            <Button
              className="postButton"
              onClick={handleChangeCorporationAlliance}
              disabled={!ccaCorporationId || !ccaNewAllianceId}
            >
              Change Corporation Alliance
            </Button>
          </div>

          <h3 className="adminH3">Change Member Corporation</h3>
          <div className="rowGroup">
            <div className="rowGroupInputs">
              <NumberInput
                label="Character ID"
                value={cmcCharacterId}
                onChange={(value) => setCmcCharacterId(value)}
                min={1}
              />
              <NumberInput
                label="New Corporation ID"
                value={cmcNewCorporationId}
                onChange={(value) => setCmcNewCorporationId(value)}
                min={1}
              />
            </div>
            <Button
              className="postButton"
              onClick={handleChangeMemberCorporation}
              disabled={!cmcCharacterId || !cmcNewCorporationId}
            >
              Change Corporation
            </Button>
          </div>

          <h3 className="adminH3">Add Member</h3>
          <div className="rowGroup">
            <div className="rowGroupInputs">
              <NumberInput
                label="Character ID"
                value={amCharacterId}
                onChange={(value) => setAmCharacterId(value)}
                min={1}
              />
              <TextInput
                label="Character Name"
                value={amCharacterName}
                onChange={(event) => setAmCharacterName(event.currentTarget.value)}
              />
              <NumberInput
                label="Corporation ID"
                value={amCorporationId}
                onChange={(value) => setAmCorporationId(value)}
                min={1}
              />
            </div>
            <Button
              className="postButton"
              onClick={handleAddMember}
              disabled={!amCharacterId || !amCharacterName || !amCorporationId}
            >
              Add Member
            </Button>
          </div>

          <div className="refreshButtons">
            <div className="refreshItem">
              <h3 className="refreshH3">Refresh kill data</h3>
              <div className="refreshTaskButton">
                <Button className="refreshButton" onClick={handleAddKills} disabled={!!taskId}>
                  {taskId ? `Task in progress... (ID: ${taskId})` : 'Start Refresh Task'}
                </Button>
              </div>
            </div>

            <div className="refreshItem">
              <h3 className="refreshH3">Refresh member data</h3>
              <div className="refreshTaskButton">
                <Button className="refreshButton" onClick={() => setModalOpened(true)} disabled={!!taskId}>
                  {taskId ? `Task in progress... (ID: ${taskId})` : 'Start Refresh Task'}
                </Button>
              </div>
            </div>

            <div className="refreshItem">
              <h3 className="refreshH3">Refresh corporation data</h3>
              <div className="refreshTaskButton">
                <Button className="refreshButton" onClick={handleRefreshCorporations} disabled={!!taskId}>
                  {taskId ? `Task in progress... (ID: ${taskId})` : 'Start Refresh Task'}
                </Button>
              </div>
            </div>
          </div>

          <Modal
            opened={modalOpened}
            onClose={() => setModalOpened(false)}
            title="Confirmation"
            centered
          >
            <p>Beware, manual edits to the members table are lost when members data is refreshed.</p>
            <Button onClick={handleConfirmRefresh} color="red" disabled={buttonsDisabled}>
              Confirm
            </Button>
            <Button onClick={() => setModalOpened(false)} style={{ marginLeft: '10px' }} disabled={buttonsDisabled}>
              Cancel
            </Button>
          </Modal>
        </Tabs.Panel>

        <Tabs.Panel value="characters" className="panel">
          <h3 className="adminH3">Add Approved Character</h3>
          <div className="rowGroup">
            <div className="rowGroupInputs">
              <NumberInput
                label="Character ID"
                value={approvedCharToAdd}
                onChange={(value) => setApprovedCharToAdd(value)}
                min={1}
              />
              <Switch
                className="adminSwitch"
                checked={addRemApproved}
                onChange={(event) => setAddRemApproved(event.currentTarget.checked)}
                onLabel="Add"
                offLabel="Remove"
                size="xl"
              />
            </div>
            <Button
              className="postButton"
              onClick={handleAddApprovedChar}
              disabled={!approvedCharToAdd}
            >
              {addRemApproved ? "Add Approved Character" : "Remove Approved" }
            </Button>
          </div>

          <h3 className="adminH3">Add Admin Character</h3>
          <div className="rowGroup">
            <div className="rowGroupInputs">
              <NumberInput
                label="Character ID"
                value={adminCharToAdd}
                onChange={(value) => setAdminCharToAdd(value)}
                min={1}
              />
              <Switch
                className="adminSwitch"
                checked={addRemAdmin}
                onChange={(event) => setAddRemAdmin(event.currentTarget.checked)}
                onLabel="Add"
                offLabel="Remove"
                size="xl"
              />
            </div>
            <Button
              className="postButton"
              onClick={handleAddAdminChar}
              disabled={!adminCharToAdd}
            >
              {addRemAdmin ? "Add Admin Character" : "Remove Admin" }
            </Button>
          </div>

          <h3 className="adminH3">Add months data via file upload</h3>
          <div className="rowGroup">
            <div className="rowGroupInputs">
              <FileInput
                label="Upload .xlsx file"
                placeholder="Click to choose"
                accept=".xlsx"
                clearable
                value={file}
                onChange={setFile}
              />
            </div>
            <Button
              className="postButton"
              onClick={handleAddMonthsData}
              disabled={!file}
            >
              Add Alliance data
            </Button>
          </div>
        </Tabs.Panel>
      </Tabs>
    </div>
  );
};