import React, { useState, useEffect } from 'react';
import { TextInput, NumberInput, Modal, Button } from '@mantine/core';
import { showNotification, cleanNotifications } from '@mantine/notifications';
import { posiNotifProps, negaNotifProps } from './helpers';
import axios from 'axios';


export default function AddDataOverlay() {
  const [acCorporationId, setAcCorporationId] = useState('');
  const [amCorporationId, setAmCorporationId] = useState('');
  const [cmcCharacterId, setCmcCharacterId] = useState('');
  const [amCharacterId, setAmCharacterId] = useState('');
  const [amCharacterName, setAmCharacterName] = useState('');
  const [cmcNewCorporationId, setCmcNewCorporationId] = useState('');
  const [taskId, setTaskId] = useState(null);
  const [modalOpened, setModalOpened] = useState(false);

  useEffect(() => {
    let interval;
    if (taskId) {
      interval = setInterval(() => {
        axios.get(`/task/status/${taskId}`)
          .then(response => {
            if (response.data.status === "Done") {
              setTaskId(null);
              cleanNotifications();
              showNotification({
                message: "Refresh task completed successfully!",
                ...posiNotifProps
              });
              clearInterval(interval);
            }
          })
          .catch(error => {
            setTaskId(null);
            cleanNotifications();
            showNotification({
              message: "Failed to check task status!",
              ...negaNotifProps
            });
            clearInterval(interval);
          });
      }, 5000);
    }
    return () => clearInterval(interval);
  }, [taskId]);

  async function handleAddCorporation() {
    try {
      await axios.post(`/corporation/add/${amCorporationId}`);
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

  async function handleConfirmRefresh() {
    setModalOpened(false);
    handleAddMembers();
  };


  return (
    <div className="adminOverlay">
      <h3 className="adminH3">Add Corporation</h3>
      <div className="rowGroup">
        <NumberInput
          className="adminInput"
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
            <Button onClick={handleAddKills} disabled={!!taskId}>
              {taskId ? `Task in progress... (ID: ${taskId})` : 'Start Refresh Task'}
            </Button>
          </div>
        </div>

        <div className="refreshItem">
          <h3 className="refreshH3">Refresh member data</h3>
          <div className="refreshTaskButton">
            <Button onClick={() => setModalOpened(true)} disabled={!!taskId}>
              {taskId ? `Task in progress... (ID: ${taskId})` : 'Start Refresh Task'}
            </Button>
          </div>
        </div>
      </div>

      <Modal
        opened={modalOpened}
        onClose={() => setModalOpened(false)}
        title="Confirmation"
      >
        <p>Beware, manual edits to the members table are lost when members is refreshed.</p>
        <Button onClick={handleConfirmRefresh} color="red">
          Confirm
        </Button>
        <Button onClick={() => setModalOpened(false)} style={{ marginLeft: '10px' }}>
          Cancel
        </Button>
      </Modal>
    </div>
  );
};