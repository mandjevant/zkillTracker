import React, { useState } from "react";
import { NavLink } from 'react-router-dom'
import { Drawer, Button } from "@mantine/core";


export default function Menu() {
  const [isActive, setIsActive] = useState(false);

  const initMenus = [
    {
      menuId: 1,
      menuName: "Corporations",
      menuRef: "/",
    },
    {
      menuId: 2,
      menuName: "Members",
      menuRef: "/members",
    },
    {
      menuId: 3,
      menuName: "Alliance",
      menuRef: "/alliance",
    },
    {
      menuId: 4,
      menuName: "Admin",
      menuRef: "/admin",
    },
  ];

  function switchActive() {
    setIsActive(!isActive);
  }

  return (
    <div className="menuHolder">
      <div className="hamburgerMenu" onClick={switchActive}>
        <span></span>
        <span></span>
        <span></span>
      </div>
      {isActive && (
        <Drawer 
          size="xs" 
          opened={isActive} 
          onClose={switchActive} 
        >
          <ul id="menu">
            {initMenus.map((menu, index) => (
              <li className="lili" key={index}>
                <NavLink 
                  to={menu.menuRef} 
                  className="navs" 
                  onClick={() => document.title = menu.menuName}
                >
                  <Button 
                    className="menuItem" 
                    variant="subtle" 
                    color="gray"
                  >
                    <label style={{ textDecoration: null }}>
                      {menu.menuName}
                    </label>
                  </Button>
                </NavLink>
              </li>
            ))}
          </ul>
        </Drawer>
      )}
    </div>
  );
}