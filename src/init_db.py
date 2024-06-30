import logging
logger = logging.getLogger(__name__)

def create_table_and_load_data(app, db, Rooms, Temperatures, Users):
    with app.app_context():
        # Ensure the tables are created
        logger.info('Setting up rooms and temperatures')
        db.create_all()

        # Check for existing rooms and only add new ones if they do not exist
        existing_rooms = {room.room_name for room in Rooms.query.all()}
        new_rooms = [
            Rooms(room_name="hall"),
            Rooms(room_name="kitchen"),
            Rooms(room_name="pooja"),
            Rooms(room_name="bathroom")
        ]
        rooms_to_add = [room for room in new_rooms if room.room_name not in existing_rooms]

        if rooms_to_add:
            logger.debug('Adding new rooms to the DB')
            db.session.add_all(rooms_to_add)
            db.session.commit()
            logger.info('Rooms loaded into DB')
        else:
            logger.info('No new rooms to add, all rooms already exist')

        # Check for existing temperatures and only add new ones if they do not exist
        existing_temperatures = {
            (temp.rooms.room_name, temp.temperature)
            for temp in Temperatures.query.join(Rooms).all()
        }
        new_temperatures = [
            Temperatures(rooms=Rooms.query.filter_by(room_name="hall").first(), temperature=17.1),
            Temperatures(rooms=Rooms.query.filter_by(room_name="hall").first(), temperature=10.3),
            Temperatures(rooms=Rooms.query.filter_by(room_name="kitchen").first(), temperature=20.5),
            Temperatures(rooms=Rooms.query.filter_by(room_name="pooja").first(), temperature=80.3),
            Temperatures(rooms=Rooms.query.filter_by(room_name="bathroom").first(), temperature=33.8)
        ]
        temperatures_to_add = [
            temp for temp in new_temperatures
            if (temp.rooms.room_name, temp.temperature) not in existing_temperatures
        ]

        if temperatures_to_add:
            logger.debug('Adding new temperatures to the DB')
            db.session.add_all(temperatures_to_add)
            db.session.commit()
            logger.info('Temperatures loaded into DB')
        else:
            logger.info('No new temperatures to add, all temperatures already exist')


# def create_table_and_load_data(app, db, Rooms, Temperatures):
#     with app.app_context():
#         if not db.engine.dialect.has_table(db.engine, 'users'):
#             logger.info('Setting up rooms')
#             db.create_all()

#             room1 = Rooms(room_name="hall")
#             room2 = Rooms(room_name="kitchen")
#             room3 = Rooms(room_name="pooja")
#             room4 = Rooms(room_name="bathroom")
        
#             temp1 = Temperatures(rooms=room1, temperature=17.1)
#             temp2 = Temperatures(rooms=room1, temperature=10.3)
#             temp3 = Temperatures(rooms=room2, temperature=20.5)
#             temp4 = Temperatures(rooms=room3, temperature=80.3)
#             temp5 = Temperatures(rooms=room4, temperature=33.8)

#             logger.debug('Loading up rooms into DB')
#             db.session.add_all([room1, room2, room3, room4])
#             db.session.add_all([temp1, temp2, temp3, temp4, temp5])
#             db.session.commit()
#             logger.info('Rooms loaded into DB')
#         else:
#             logger.info('Rooms table already exists')