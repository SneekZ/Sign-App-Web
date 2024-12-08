import React, { useState, useEffect } from "react";
import { Select, Button, Flex, Modal } from "antd";
import SignsTable from "./SignsTable.jsx";
import LoadingGif from "../animations/loading.gif";

const api_url = "http://localhost:52911/";
const test_url = "http://localhost:8000/signs/";

const LpuSelector = () => {
  const [loading, setLoading] = useState("Загрузить данные");

  const [isModalOpen, setModalOpen] = useState(false);
  const [modalText, setModalText] = useState("");

  async function getLpu() {
    try {
      const response = await fetch(api_url + "lpu");
      if (!response.ok) {
        alert(response.statusText);
      }
      return await response.json();
    } catch (error) {
      alert(error);
    }
  }

  const [lpuData, setLpuData] = useState([{}]);

  useEffect(() => {
    const loadLpuData = async () => {
      const data = await getLpu();
      if (data.error_msg) {
        setModalText(data.error_msg);
        setModalOpen(true);
        return;
      }
      setLpuData(data.lpudata);
    };
    loadLpuData();
  }, []);

  const [lpuId, setLpuId] = useState(1);

  const handleChange = (value) => {
    setLpuId(value);
  };

  const [signsData, setSignsData] = useState(null);

  async function getSigns(id) {
    try {
      const response = await fetch(test_url + id);
      if (!response.ok) {
        alert(response.statusText);
      }
      return await response.json();
    } catch (error) {
      alert(error);
    }
  }

  const handleClick = async () => {
    setLoading(
      <img src={LoadingGif} alt="loading gif" width="180" height="180" />,
    );
    const signsData = await getSigns(lpuId);
    if (signsData.error_msg) {
      setModalText(signsData.error_msg);
      setModalOpen(true);
      setLoading("Загрузить данные");
      return;
    }
    setSignsData(signsData.signs);
    setLoading("Загрузить данные");
  };

  return (
    <div>
      <Flex gap="middle" wrap>
        <Select
          onChange={handleChange}
          className="lpu_selector"
          showSearch
          placeholder="Search to Select"
          optionFilterProp="label"
          filterSort={(optionA, optionB) =>
            (optionA?.label ?? "")
              .toLowerCase()
              .localeCompare((optionB?.label ?? "").toLowerCase())
          }
          options={lpuData}
        />
        <Button className="lpu_selector_button" onClick={handleClick}>
          {loading}
        </Button>
        <Modal
          title="Возникла ошибка при получении данных"
          open={isModalOpen}
          onOk={() => setModalOpen(false)}
          footer={(_, { OkBtn, CancelBtn }) => (
            <>
              <OkBtn />
            </>
          )}
        >
          <p>{modalText}</p>
        </Modal>
      </Flex>
      <SignsTable data={signsData} />
    </div>
  );
};
export default LpuSelector;
