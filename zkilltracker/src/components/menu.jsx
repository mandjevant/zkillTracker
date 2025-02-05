import React, { useEffect, useState } from "react";
import { NavLink } from 'react-router-dom'
import { Drawer, Button } from "@mantine/core";
import { useAuth } from "../App";


const initMenus = [
  {
    menuId: 1,
    menuName: "Corporations",
    menuRef: "/corporation",
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
];

const memberMenus = [
  {
    menuId: 1,
    menuName: "Corporations",
    menuRef: "/corporation",
  },
  {
    menuId: 2,
    menuName: "Members",
    menuRef: "/members",
  },
];

const adminMenus = [
  {
    menuId: 4,
    menuName: "Admin",
    menuRef: "/admin",
  },
];

export default function Menu() {
  const [isActive, setIsActive] = useState(false);
  const [menus, setMenus] = useState([initMenus]);
  const { isAdmin, isMember } = useAuth()

  useEffect(() => {
    if (isAdmin) {
      setMenus(initMenus.concat(adminMenus))
    } else if (isMember) {
      setMenus(memberMenus)
    } else {
      setMenus(initMenus)
    }
  }, [isAdmin, isMember])

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
            {menus.map((menu, index) => (
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