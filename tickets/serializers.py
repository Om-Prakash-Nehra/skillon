from rest_framework import serializers
from .models import User, Ticket, Comment, Timeline

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','email','password','role']
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email',''),
            role=validated_data.get('role','user')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id','ticket','user','content','created_at']
        read_only_fields = ['id','ticket','user','created_at']

class TimelineSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Timeline
        fields = ['id','action','user','created_at']

class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    timeline = TimelineSerializer(many=True, read_only=True)
    sla_breached = serializers.SerializerMethodField()
    class Meta:
        model = Ticket
        fields = ['id','title','description','priority','sla_hours','created_by','assigned_to','status','version','created_at','updated_at','comments','timeline','sla_breached']
    def get_sla_breached(self,obj):
        return obj.is_breached()
