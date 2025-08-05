import React, { useState, useEffect } from 'react';
import { TextInput, NumberInput, Modal, Button, Switch, Tabs, FileInput } from '@mantine/core';
import { showNotification } from '@mantine/notifications';
import { posiNotifProps, negaNotifProps } from './helpers';
import { useAuth } from '../App';


export default function AddDataOverlay() {
  const [acCorporationId, setAcCorporationId] = useState('');
  const [amCorporationId, setAmCorporationId] = useState('');
  const [cmcCharacterId, setCmcCharacterId] = useState('');
  const [amCharacterId, setAmCharacterId] = useState('');
  const [amCharacterName, setAmCharacterName] = useState('');
  const [cmcNewCorporationId, setCmcNewCorporationId] = useState('');
  const [approvedCharToAdd, setApprovedCharToAdd] = useState('');
  const [approvedMemberToAdd, setApprovedMemberToAdd] = useState('');
  const [approvedCorpToRem, setApprovedCorpToRem] = useState('');
  const [adminCharToAdd, setAdminCharToAdd] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [modalOpened, setModalOpened] = useState(false);
  const [addRemApproved, setAddRemApproved] = useState(true);
  const [addRemApprovedMember, setAddRemApprovedMember] = useState(true);
  const [addRemAdmin, setAddRemAdmin] = useState(true);
  const [buttonsDisabled, setButtonsDisabled] = useState(false);
  const [ccaCorporationId, setCcaCorporationId] = useState('');
  const [ccaNewAllianceId, setCcaNewAllianceId] = useState('');
  const [file, setFile] = useState(null);
  const { axiosInstance } = useAuth();

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
      await axiosInstance.post(`/corporation/add/${acCorporationId}`);
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
      await axiosInstance.post(`/member/${cmcCharacterId}/change_corporation/${cmcNewCorporationId}`);
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
      await axiosInstance.put(`/corporation/${ccaCorporationId}/change_alliance/${ccaNewAllianceId}`);
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
      await axiosInstance.post(`/members/add/${amCharacterId}/${amCharacterName}/${amCorporationId}`);
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
      const response = await axiosInstance.get(`/kills/add`);
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
      const response = await axiosInstance.get(`/corporations/refresh`);
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
      const response = await axiosInstance.get(`/members/add`);
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
        await axiosInstance.post(`/approved/add/${approvedCharToAdd}`);
      } else {
        await axiosInstance.post(`/approved/remove/${approvedCharToAdd}`);
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

  async function handleRemoveApprovedCorp() {
    try {
      await axiosInstance.post(`/approved/remove/corp/${approvedCorpToRem}`)
      showNotification({
        message: `Approved corporation removed successfully!`,
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: `Failed to remove approved corporation!`,
        ...negaNotifProps
      });
    }
  }

  async function handleAddMemberChar() {
    try {
      if (addRemApprovedMember) {
        await axiosInstance.post(`/approved_member/add/${approvedMemberToAdd}`);
      } else {
        await axiosInstance.post(`/approved_member/remove/${approvedMemberToAdd}`);
      }
      showNotification({
        message: `Approved member ${ addRemApprovedMember ? "added" : "removed" } successfully!`,
        ...posiNotifProps
      });
    } catch (error) {
      showNotification({
        message: `Failed to ${ addRemApprovedMember ? "add" : "remove" } approved member!`,
        ...negaNotifProps
      });
    }
  }

  async function handleAddAdminChar() {
    try {
      if (addRemAdmin) {
        await axiosInstance.post(`/admin/add/${adminCharToAdd}`);
      } else {
        await axiosInstance.post(`/admin/remove/${adminCharToAdd}`);
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
        message: "Please select a .XLSX file before uploading",
        ...negaNotifProps
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    axiosInstance.post('/upload_file', formData, {
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
        message: "Error uploading XLSX file",
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
          <h3 className="adminH3">Remove approved characters by corp</h3>
          <div className="rowGroup">
            <div className="rowGroupInputs">
              <NumberInput
                label="Corporation ID"
                value={approvedCorpToRem}
                onChange={(value) => setApprovedCorpToRem(value)}
                min={1}
              />
            </div>
            <Button
              className="postButton"
              onClick={handleRemoveApprovedCorp}
              disabled={!approvedCorpToRem}
            >
              Remove Approved Corporation
            </Button>
          </div>

          <h3 className="adminH3">Add Approved Member (no leadership)</h3>
          <div className="rowGroup">
            <div className="rowGroupInputs">
              <NumberInput
                label="Character ID"
                value={approvedMemberToAdd}
                onChange={(value) => setApprovedMemberToAdd(value)}
                min={1}
              />
              <Switch
                className="adminSwitch"
                checked={addRemApprovedMember}
                onChange={(event) => setAddRemApprovedMember(event.currentTarget.checked)}
                onLabel="Add"
                offLabel="Remove"
                size="xl"
              />
            </div>
            <Button
              className="postButton"
              onClick={handleAddMemberChar}
              disabled={!approvedMemberToAdd}
            >
              {addRemApproved ? "Add Approved Member" : "Remove Approved" }
            </Button>
          </div>

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