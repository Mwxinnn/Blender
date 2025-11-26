import bpy
import mathutils

car = bpy.data.objects['Car1']

# 清除旧动画
if car.animation_data:
    car.animation_data_clear()

# 确保有刚体
if not car.rigid_body:
    bpy.context.view_layer.objects.active = car
    bpy.ops.rigidbody.object_add()

# 设置刚体属性
car.rigid_body.type = 'ACTIVE'
car.rigid_body.mass = 1
car.rigid_body.collision_shape = 'CONVEX_HULL'
car.rigid_body.linear_damping = 0.04  # 降低阻尼
car.rigid_body.angular_damping = 0.1

# 计算方向和速度
rotation_matrix = car.rotation_euler.to_matrix()
local_neg_y = rotation_matrix @ mathutils.Vector((0, -1, 0))
speed = 1  # m/s
fps = bpy.context.scene.render.fps

# 第1帧：kinematic模式
bpy.context.scene.frame_set(1)
start_loc = car.location.copy()
car.rigid_body.kinematic = True
car.keyframe_insert(data_path="location", frame=1)
car.keyframe_insert(data_path="rigid_body.kinematic", frame=1)

# 第2-10帧：用多帧建立速度（关键改进）
num_frames = 10  # 使用更多帧来建立速度
for i in range(1, num_frames + 1):
    frame = i + 1
    time_delta = i / fps
    displacement = local_neg_y * speed * time_delta
    new_loc = start_loc + displacement
    
    bpy.context.scene.frame_set(frame)
    car.location = new_loc
    car.keyframe_insert(data_path="location", frame=frame)

# 第11帧：切换到ACTIVE
bpy.context.scene.frame_set(num_frames + 2)
car.rigid_body.kinematic = False
car.keyframe_insert(data_path="rigid_body.kinematic", frame=num_frames + 2)

# 设置线性插值
if car.animation_data and car.animation_data.action:
    for fcurve in car.animation_data.action.fcurves:
        if fcurve.data_path == "location":
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'LINEAR'

bpy.context.scene.frame_set(1)
print("Setup complete! Car will accelerate for first 10 frames then physics takes over.")